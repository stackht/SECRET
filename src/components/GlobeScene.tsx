import { useEffect, useRef } from "react";
import * as THREE from "three";

const vertexShader = `
  attribute float size;
  attribute float pulse;
  varying float vPulse;
  void main() {
    vPulse = pulse;
    vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
    gl_PointSize = size * (220.0 / -mvPosition.z);
    gl_Position = projectionMatrix * mvPosition;
  }
`;

const fragmentShader = `
  varying float vPulse;
  void main() {
    vec2 c = gl_PointCoord - vec2(0.5);
    float d = length(c);
    float alpha = smoothstep(0.5, 0.0, d) * (0.55 + vPulse * 0.45);
    vec3 color = mix(vec3(0.35, 0.72, 1.0), vec3(0.72, 0.42, 1.0), vPulse);
    gl_FragColor = vec4(color, alpha);
  }
`;

function toVec(lat: number, lon: number, radius: number) {
  const phi = (90 - lat) * (Math.PI / 180);
  const theta = (lon + 180) * (Math.PI / 180);
  return new THREE.Vector3(
    -(radius * Math.sin(phi) * Math.cos(theta)),
    radius * Math.cos(phi),
    radius * Math.sin(phi) * Math.sin(theta)
  );
}

export function GlobeScene() {
  const hostRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const host = hostRef.current;
    if (!host) return;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(32, host.clientWidth / host.clientHeight, 0.1, 100);
    camera.position.set(0, 0, 6.8);

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.75));
    renderer.setSize(host.clientWidth, host.clientHeight);
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    host.appendChild(renderer.domElement);

    const root = new THREE.Group();
    root.scale.setScalar(0.84);
    scene.add(root);

    const shell = new THREE.Mesh(
      new THREE.SphereGeometry(2.05, 48, 48),
      new THREE.MeshBasicMaterial({ color: "#7b61ff", transparent: true, opacity: 0.05, wireframe: true })
    );
    root.add(shell);

    const pointCount = 5200;
    const positions = new Float32Array(pointCount * 3);
    const sizes = new Float32Array(pointCount);
    const pulses = new Float32Array(pointCount);
    for (let i = 0; i < pointCount; i += 1) {
      const a = Math.random() * Math.PI * 2;
      const b = Math.acos(2 * Math.random() - 1);
      const r = 2.02 + Math.random() * 0.06;
      positions[i * 3] = r * Math.sin(b) * Math.cos(a);
      positions[i * 3 + 1] = r * Math.cos(b);
      positions[i * 3 + 2] = r * Math.sin(b) * Math.sin(a);
      sizes[i] = 1.8 + Math.random() * 2.6;
      pulses[i] = Math.random();
    }

    const pointGeometry = new THREE.BufferGeometry();
    pointGeometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));
    pointGeometry.setAttribute("size", new THREE.BufferAttribute(sizes, 1));
    pointGeometry.setAttribute("pulse", new THREE.BufferAttribute(pulses, 1));

    const pointMaterial = new THREE.ShaderMaterial({
      vertexShader,
      fragmentShader,
      transparent: true,
      depthWrite: false,
      blending: THREE.AdditiveBlending
    });
    const pointCloud = new THREE.Points(pointGeometry, pointMaterial);
    root.add(pointCloud);

    const arcGroup = new THREE.Group();
    const arcs: Array<[[number, number], [number, number], string]> = [
      [[14, 96], [44, 4], "#7be9ff"],
      [[28, 66], [-10, 128], "#a46dff"],
      [[-6, 94], [46, -96], "#d16cff"],
      [[8, 38], [26, 18], "#67dfff"],
      [[-18, -20], [35, 86], "#7b8aff"]
    ];
    arcs.forEach(([start, end, color]) => {
      const a = toVec(start[0], start[1], 2.02);
      const b = toVec(end[0], end[1], 2.02);
      const mid = a.clone().add(b).multiplyScalar(0.5).normalize().multiplyScalar(2.55);
      const curve = new THREE.QuadraticBezierCurve3(a, mid, b);
      const geometry = new THREE.BufferGeometry().setFromPoints(curve.getPoints(90));
      arcGroup.add(new THREE.Line(geometry, new THREE.LineBasicMaterial({ color, transparent: true, opacity: 0.38, blending: THREE.AdditiveBlending })));
    });
    root.add(arcGroup);

    const contourSets = [
      [
        new THREE.Vector3(-1.25, 0.56, 1.32),
        new THREE.Vector3(-0.88, 0.82, 1.48),
        new THREE.Vector3(-0.12, 0.98, 1.62),
        new THREE.Vector3(0.62, 0.7, 1.56),
        new THREE.Vector3(1.1, 0.25, 1.42),
        new THREE.Vector3(0.84, -0.62, 1.46),
        new THREE.Vector3(0.12, -0.92, 1.58),
        new THREE.Vector3(-0.72, -0.82, 1.56),
        new THREE.Vector3(-1.2, -0.1, 1.4),
        new THREE.Vector3(-1.25, 0.56, 1.32)
      ],
      [
        new THREE.Vector3(-0.34, 0.28, 1.78),
        new THREE.Vector3(0.06, 0.48, 1.84),
        new THREE.Vector3(0.46, 0.18, 1.75),
        new THREE.Vector3(0.42, -0.22, 1.72),
        new THREE.Vector3(-0.08, -0.3, 1.8),
        new THREE.Vector3(-0.34, 0.28, 1.78)
      ]
    ];
    contourSets.forEach((set, idx) => {
      root.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(set), new THREE.LineBasicMaterial({ color: idx === 0 ? "#b981ff" : "#7ce8ff", transparent: true, opacity: 0.52 })));
    });

    const orbitalRingMaterial = new THREE.LineBasicMaterial({ color: "#6179ff", transparent: true, opacity: 0.24 });
    [2.35, 2.62, 2.88].forEach((radius, i) => {
      const curve = new THREE.EllipseCurve(0, 0, radius, radius * (0.34 + i * 0.08), 0, Math.PI * 2, false, 0);
      const line = new THREE.LineLoop(
        new THREE.BufferGeometry().setFromPoints(curve.getPoints(180).map((p) => new THREE.Vector3(p.x, p.y, 0))),
        orbitalRingMaterial
      );
      line.rotation.x = 1.15 + i * 0.18;
      line.rotation.y = 0.24 + i * 0.28;
      root.add(line);
    });

    const flare = new THREE.Sprite(
      new THREE.SpriteMaterial({
        map: new THREE.CanvasTexture(makeGlowCanvas()),
        color: "#bff6ff",
        transparent: true,
        opacity: 0.86,
        blending: THREE.AdditiveBlending
      })
    );
    flare.scale.set(1.8, 1.8, 1.8);
    flare.position.set(0.82, 0.44, 1.22);
    root.add(flare);

    const ambient = new THREE.AmbientLight("#7acfff", 0.42);
    const violet = new THREE.PointLight("#bb67ff", 9, 18);
    violet.position.set(-2.8, 1.8, 2.8);
    const cyan = new THREE.PointLight("#59dfff", 8, 18);
    cyan.position.set(2.2, -0.4, 3.2);
    scene.add(ambient, violet, cyan);

    const bgParticles = new THREE.Points(
      new THREE.BufferGeometry().setAttribute(
        "position",
        new THREE.Float32BufferAttribute(Array.from({ length: 1400 * 3 }, () => (Math.random() - 0.5) * 18), 3)
      ),
      new THREE.PointsMaterial({ color: "#8fa3ff", size: 0.01, transparent: true, opacity: 0.28 })
    );
    scene.add(bgParticles);

    const pointer = { x: 0, y: 0 };
    const onMove = (event: PointerEvent) => {
      const rect = renderer.domElement.getBoundingClientRect();
      pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
      pointer.y = ((event.clientY - rect.top) / rect.height) * 2 - 1;
      host.style.cursor = "grab";
    };
    const onLeave = () => {
      pointer.x = 0;
      pointer.y = 0;
      host.style.cursor = "default";
    };
    host.addEventListener("pointermove", onMove);
    host.addEventListener("pointerleave", onLeave);

    let raf = 0;
    const animate = () => {
      raf = requestAnimationFrame(animate);
      const t = performance.now() * 0.00022;
      root.rotation.y = t + pointer.x * 0.2;
      root.rotation.x = Math.sin(t * 1.8) * 0.04 - pointer.y * 0.12;
      arcGroup.rotation.y = -t * 1.35;
      flare.material.rotation = t * 0.6;
      flare.scale.setScalar(1.6 + Math.sin(t * 6.5) * 0.08);
      const pulseAttr = pointGeometry.getAttribute("pulse") as THREE.BufferAttribute;
      for (let i = 0; i < pointCount; i += 1) {
        pulseAttr.array[i] = 0.45 + 0.55 * Math.sin(t * 9 + i * 0.017);
      }
      pulseAttr.needsUpdate = true;
      renderer.render(scene, camera);
    };
    animate();

    const onResize = () => {
      const w = host.clientWidth;
      const h = host.clientHeight;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    };
    window.addEventListener("resize", onResize);

    return () => {
      cancelAnimationFrame(raf);
      window.removeEventListener("resize", onResize);
      host.removeEventListener("pointermove", onMove);
      host.removeEventListener("pointerleave", onLeave);
      pointGeometry.dispose();
      pointMaterial.dispose();
      renderer.dispose();
      host.removeChild(renderer.domElement);
    };
  }, []);

  return (
    <div className="globe-shell">
      <div ref={hostRef} className="globe-canvas-host" />
      <div className="globe-scanlines" />
      <div className="globe-vignette" />
    </div>
  );
}

function makeGlowCanvas() {
  const canvas = document.createElement("canvas");
  canvas.width = 256;
  canvas.height = 256;
  const ctx = canvas.getContext("2d");
  if (!ctx) return canvas;
  const gradient = ctx.createRadialGradient(128, 128, 10, 128, 128, 128);
  gradient.addColorStop(0, "rgba(220,250,255,1)");
  gradient.addColorStop(0.2, "rgba(121,226,255,0.85)");
  gradient.addColorStop(0.5, "rgba(121,120,255,0.3)");
  gradient.addColorStop(1, "rgba(0,0,0,0)");
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, 256, 256);
  return canvas;
}
