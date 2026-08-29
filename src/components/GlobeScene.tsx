import { useEffect, useMemo, useRef, useState } from "react";
import * as THREE from "three";

type GlobeNode = {
  id: string;
  label: string;
  lat: number;
  lon: number;
};

const INCIDENTS: GlobeNode[] = [
  { id: "kandivali-west", label: "Kandivali West Case", lat: 19.208, lon: 72.842 },
  { id: "malad", label: "Malad Node", lat: 19.186, lon: 72.848 },
  { id: "borivali", label: "Borivali Link", lat: 19.230, lon: 72.856 },
  { id: "andheri", label: "Andheri Spur", lat: 19.119, lon: 72.846 },
  { id: "bandra", label: "Bandra Trace", lat: 19.059, lon: 72.829 },
  { id: "south-mumbai", label: "South Mumbai Anchor", lat: 18.939, lon: 72.835 },
];

const ROUTES: Record<string, string[]> = {
  "kandivali-west": ["malad", "borivali", "andheri", "bandra"],
  "malad": ["kandivali-west", "andheri", "south-mumbai"],
  "borivali": ["kandivali-west", "bandra"],
  "andheri": ["kandivali-west", "bandra", "south-mumbai"],
  "bandra": ["andheri", "south-mumbai"],
  "south-mumbai": ["bandra", "andheri", "malad"]
};

function degreesToRadians(deg: number) {
  return (deg * Math.PI) / 180;
}

function latLonToVector3(lat: number, lon: number, radius: number) {
  const phi = degreesToRadians(90 - lat);
  const theta = degreesToRadians(lon + 180);
  return new THREE.Vector3(
    -(radius * Math.sin(phi) * Math.cos(theta)),
    radius * Math.cos(phi),
    radius * Math.sin(phi) * Math.sin(theta)
  );
}

function makeSpriteTexture(inner = "rgba(232,248,255,1)", middle = "rgba(80,166,255,0.9)", outer = "rgba(63,115,255,0)") {
  const canvas = document.createElement("canvas");
  canvas.width = 128;
  canvas.height = 128;
  const ctx = canvas.getContext("2d");
  if (!ctx) return new THREE.CanvasTexture(canvas);
  const gradient = ctx.createRadialGradient(64, 64, 4, 64, 64, 64);
  gradient.addColorStop(0, inner);
  gradient.addColorStop(0.22, middle);
  gradient.addColorStop(0.6, outer);
  gradient.addColorStop(1, "rgba(0,0,0,0)");
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, 128, 128);
  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  return texture;
}

function makeGoldSpriteTexture() {
  const canvas = document.createElement("canvas");
  canvas.width = 128;
  canvas.height = 128;
  const ctx = canvas.getContext("2d");
  if (!ctx) return new THREE.CanvasTexture(canvas);
  const gradient = ctx.createRadialGradient(64, 64, 2, 64, 64, 64);
  gradient.addColorStop(0, "rgba(255,246,202,1)");
  gradient.addColorStop(0.16, "rgba(255,214,92,0.95)");
  gradient.addColorStop(0.44, "rgba(255,170,44,0.65)");
  gradient.addColorStop(1, "rgba(0,0,0,0)");
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, 128, 128);
  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  return texture;
}

function makeArc(start: THREE.Vector3, end: THREE.Vector3, lift = 0.68) {
  const mid = start.clone().add(end).multiplyScalar(0.5).normalize().multiplyScalar(2.4 + lift);
  const curve = new THREE.QuadraticBezierCurve3(start, mid, end);
  return new THREE.BufferGeometry().setFromPoints(curve.getPoints(72));
}

function makeFallbackEarthTexture() {
  const canvas = document.createElement("canvas");
  canvas.width = 1024;
  canvas.height = 512;
  const ctx = canvas.getContext("2d");
  if (!ctx) return new THREE.CanvasTexture(canvas);

  const ocean = ctx.createLinearGradient(0, 0, 0, 512);
  ocean.addColorStop(0, "#173d9e");
  ocean.addColorStop(1, "#0a1d5a");
  ctx.fillStyle = ocean;
  ctx.fillRect(0, 0, 1024, 512);

  const glow = ctx.createRadialGradient(580, 190, 20, 580, 190, 420);
  glow.addColorStop(0, "rgba(104,192,255,0.28)");
  glow.addColorStop(1, "rgba(0,0,0,0)");
  ctx.fillStyle = glow;
  ctx.fillRect(0, 0, 1024, 512);

  ctx.fillStyle = "#204b2f";
  const land = (x: number, y: number, w: number, h: number, r: number) => {
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.arcTo(x + w, y, x + w, y + h, r);
    ctx.arcTo(x + w, y + h, x, y + h, r);
    ctx.arcTo(x, y + h, x, y, r);
    ctx.arcTo(x, y, x + w, y, r);
    ctx.closePath();
    ctx.fill();
  };
  land(150, 90, 210, 80, 40);
  land(310, 150, 170, 70, 28);
  land(470, 120, 250, 95, 36);
  land(705, 170, 150, 60, 26);
  land(775, 250, 105, 160, 40);
  land(240, 270, 180, 150, 42);
  land(530, 300, 220, 110, 36);

  ctx.strokeStyle = "rgba(255,255,255,0.08)";
  ctx.lineWidth = 3;
  for (let i = 0; i < 8; i += 1) {
    ctx.beginPath();
    ctx.moveTo(0, i * 64);
    ctx.lineTo(1024, i * 64);
    ctx.stroke();
  }
  for (let i = 0; i < 16; i += 1) {
    ctx.beginPath();
    ctx.moveTo(i * 64, 0);
    ctx.lineTo(i * 64, 512);
    ctx.stroke();
  }

  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  return texture;
}

function resolveTextureUrl(path: string) {
  return new URL(path, window.location.href).toString();
}

export function GlobeScene() {
  const hostRef = useRef<HTMLDivElement | null>(null);
  const hitAreaRef = useRef<THREE.Points | null>(null);
  const [selectedId, setSelectedId] = useState("kandivali-west");
  const selectedIdRef = useRef(selectedId);

  const selectedIncident = useMemo(() => INCIDENTS.find((item) => item.id === selectedId) ?? INCIDENTS[0], [selectedId]);

  useEffect(() => {
    selectedIdRef.current = selectedId;
  }, [selectedId]);

  useEffect(() => {
    const host = hostRef.current;
    if (!host) return;

    const scene = new THREE.Scene();
    scene.background = null;
    const camera = new THREE.PerspectiveCamera(34, host.clientWidth / host.clientHeight, 0.1, 100);
    camera.position.set(0, 0, 9.2);

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.75));
    renderer.setSize(host.clientWidth, host.clientHeight);
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    renderer.setClearColor(0x000000, 0);
    host.appendChild(renderer.domElement);
    host.style.pointerEvents = "auto";
    host.style.touchAction = "none";
    host.style.cursor = "grab";

    const root = new THREE.Group();
    root.scale.setScalar(0.5);
    root.rotation.z = degreesToRadians(23.4);
    scene.add(root);
    const rotationState = { x: 0, y: 0 };
    const spinBase = { x: 0, y: 0 };

    const loader = new THREE.TextureLoader();
    const dayMap = loader.load(resolveTextureUrl("textures/earth_day.jpg"));
    const specMap = loader.load(resolveTextureUrl("textures/earth_specular.jpg"));
    const nightMap = loader.load(resolveTextureUrl("textures/earth_night.png"));
    const cloudMap = loader.load(resolveTextureUrl("textures/earth_clouds.png"));
    [dayMap, specMap, nightMap, cloudMap].forEach((texture) => {
      texture.colorSpace = THREE.SRGBColorSpace;
      texture.anisotropy = renderer.capabilities.getMaxAnisotropy();
    });

    const earthGroup = new THREE.Group();
    root.add(earthGroup);

    const earthGeometry = new THREE.SphereGeometry(3.6, 64, 64);
    const earthMaterial = new THREE.MeshPhongMaterial({
      map: dayMap,
      specularMap: specMap,
      specular: new THREE.Color(0x3a4f86),
      shininess: 22,
      emissive: new THREE.Color(0x000000),
      emissiveMap: null,
      emissiveIntensity: 0,
    });
    const earth = new THREE.Mesh(earthGeometry, earthMaterial);
    earthGroup.add(earth);

    const cloudsGeometry = new THREE.SphereGeometry(3.6 * 1.02, 64, 64);
    const cloudsMaterial = new THREE.MeshPhongMaterial({
      map: cloudMap,
      transparent: true,
      opacity: 0.12,
      depthWrite: false,
    });
    const clouds = new THREE.Mesh(cloudsGeometry, cloudsMaterial);
    earthGroup.add(clouds);

    const caseRings: THREE.Mesh[] = [];
    const hitMarkers: THREE.Mesh[] = [];
    const incidentTexture = makeGoldSpriteTexture();
    const incidentGeometry = new THREE.BufferGeometry();
    const incidentPositions = new Float32Array(INCIDENTS.length * 3);
    const incidentSizes = new Float32Array(INCIDENTS.length);
    INCIDENTS.forEach((incident, index) => {
      const v = latLonToVector3(incident.lat, incident.lon, 3.72);
      incidentPositions[index * 3] = v.x;
      incidentPositions[index * 3 + 1] = v.y;
      incidentPositions[index * 3 + 2] = v.z;
      incidentSizes[index] = incident.id === selectedId ? 1.8 : 1.05;

      const ring = new THREE.Mesh(
        new THREE.RingGeometry(0.010, 0.018, 16),
        new THREE.MeshBasicMaterial({
          color: incident.id === selectedId ? 0xffd46a : 0xffb13b,
          transparent: true,
          opacity: incident.id === selectedId ? 0.18 : 0.08,
          side: THREE.DoubleSide,
          depthWrite: false,
          blending: THREE.AdditiveBlending
        })
      );
      ring.position.copy(v.clone().normalize().multiplyScalar(3.76));
      ring.lookAt(0, 0, 0);
      ring.scale.setScalar(incident.id === selectedId ? 1.45 : 1.0);
      caseRings.push(ring);
      earthGroup.add(ring);

      const hitMarker = new THREE.Mesh(
        new THREE.SphereGeometry(0.05, 8, 8),
        new THREE.MeshBasicMaterial({
          color: 0x000000,
          transparent: true,
          opacity: 0.01,
          depthWrite: false
        })
      );
      hitMarker.position.copy(v.clone().normalize().multiplyScalar(3.72));
      hitMarker.userData = { id: incident.id };
      hitMarkers.push(hitMarker);
      earthGroup.add(hitMarker);
    });
    incidentGeometry.setAttribute("position", new THREE.BufferAttribute(incidentPositions, 3));
    incidentGeometry.setAttribute("size", new THREE.BufferAttribute(incidentSizes, 1));

    const incidentPoints = new THREE.Points(
      incidentGeometry,
      new THREE.ShaderMaterial({
        transparent: true,
        depthWrite: false,
        blending: THREE.AdditiveBlending,
        uniforms: { map: { value: incidentTexture } },
        vertexShader: `
          attribute float size;
          varying float vSize;
          void main() {
            vSize = size;
            vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
            gl_PointSize = size * (120.0 / -mvPosition.z);
            gl_Position = projectionMatrix * mvPosition;
          }
        `,
        fragmentShader: `
          uniform sampler2D map;
          void main() {
            vec4 tex = texture2D(map, gl_PointCoord);
            gl_FragColor = tex;
          }
        `
      })
    );
    root.add(incidentPoints);
    hitAreaRef.current = incidentPoints;

    const lineMaterial = new THREE.LineBasicMaterial({
      color: 0x63dfff,
      transparent: true,
      opacity: 0.65,
      blending: THREE.AdditiveBlending
    });
    const routeGroup = new THREE.Group();
    root.add(routeGroup);
    const routeLines: Array<{ line: THREE.Line; glow: THREE.Line }> = [];
    const routeGeometries: THREE.BufferGeometry[] = [];
    Object.entries(ROUTES).forEach(([fromId, targets]) => {
      const from = INCIDENTS.find((item) => item.id === fromId);
      if (!from) return;
      const a = latLonToVector3(from.lat, from.lon, 3.7);
      targets.forEach((targetId, idx) => {
        const to = INCIDENTS.find((item) => item.id === targetId);
        if (!to) return;
        const b = latLonToVector3(to.lat, to.lon, 3.7);
        const geom = makeArc(a, b, 0.5 + idx * 0.08);
        const glowGeom = geom.clone();
        const line = new THREE.Line(geom, lineMaterial.clone());
        const glow = new THREE.Line(
          glowGeom,
          new THREE.LineBasicMaterial({
            color: 0x9af7ff,
            transparent: true,
            opacity: 0.18,
            blending: THREE.AdditiveBlending
          })
        );
        line.visible = fromId === selectedIdRef.current || targetId === selectedIdRef.current;
        glow.visible = line.visible;
        routeGeometries.push(geom);
        routeLines.push({ line, glow });
        routeGroup.add(line);
        routeGroup.add(glow);
      });
    });

    const flare = new THREE.Sprite(
      new THREE.SpriteMaterial({
        map: makeSpriteTexture("rgba(255,255,255,1)", "rgba(102,219,255,0.92)", "rgba(63,115,255,0)"),
        color: 0x98f4ff,
        transparent: true,
        opacity: 0.55,
        blending: THREE.AdditiveBlending
      })
    );
    flare.position.copy(latLonToVector3(selectedIncident.lat, selectedIncident.lon, 3.95));
    flare.scale.set(0.22, 0.22, 0.22);
      earthGroup.add(flare);

    const bgParticles = new THREE.Points(
      new THREE.BufferGeometry().setAttribute(
        "position",
        new THREE.Float32BufferAttribute(
          Array.from({ length: 1200 * 3 }, (_, i) => Math.sin(i * 12.9898) * 10.0),
          3
        )
      ),
      new THREE.PointsMaterial({ color: 0x89a8ff, size: 0.012, transparent: true, opacity: 0.12 })
    );
    scene.add(bgParticles);

    const ambient = new THREE.AmbientLight(0x25324a, 0.65);
    const directionalLight = new THREE.DirectionalLight(0xffffff, 1.7);
    directionalLight.position.set(6, 4, 6);
    const rimLight = new THREE.DirectionalLight(0x4aa7ff, 0.52);
    rimLight.position.set(-6, -2, -4);
    scene.add(ambient, directionalLight, rimLight);

    const raycaster = new THREE.Raycaster();
    const pointer = new THREE.Vector2();
    const dragState = { active: false, x: 0, y: 0, startRotX: 0, startRotY: 0 };
    const updatePointer = (event: PointerEvent) => {
      const rect = renderer.domElement.getBoundingClientRect();
      pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
      pointer.y = -(((event.clientY - rect.top) / rect.height) * 2 - 1);
    };
    const onPointerMove = (event: PointerEvent) => {
      updatePointer(event);
      if (!dragState.active) return;
      const dx = event.clientX - dragState.x;
      const dy = event.clientY - dragState.y;
      rotationState.y = dragState.startRotY + dx * 0.004;
      rotationState.x = dragState.startRotX + dy * 0.0035;
      root.rotation.y = rotationState.y;
      root.rotation.x = rotationState.x;
      event.preventDefault();
    };
    const onPointerUp = () => {
      const t = performance.now() * 0.00022;
      spinBase.y = rotationState.y - t * 0.12;
      spinBase.x = rotationState.x - Math.sin(t * 0.22) * 0.06;
      dragState.active = false;
      host.style.cursor = "grab";
    };
    const onPointerDown = (event: PointerEvent) => {
      updatePointer(event);
      dragState.active = true;
      dragState.x = event.clientX;
      dragState.y = event.clientY;
      dragState.startRotX = rotationState.x;
      dragState.startRotY = rotationState.y;
      host.style.cursor = "grabbing";
      event.preventDefault();
      if (pointer.x < -1 || pointer.x > 1 || pointer.y < -1 || pointer.y > 1) return;
      raycaster.setFromCamera(pointer, camera);
      const hits = raycaster.intersectObjects(hitMarkers, true);
      if (!hits.length) return;
      const hit = hits[0];
      const next = INCIDENTS.find((incident) => incident.id === hit.object.userData.id);
      if (next) setSelectedId(next.id);
    };

    window.addEventListener("pointermove", onPointerMove);
    window.addEventListener("pointerup", onPointerUp);
    window.addEventListener("pointerdown", onPointerDown);

    let raf = 0;
    const animate = () => {
      raf = requestAnimationFrame(animate);
      const t = performance.now() * 0.00022;
      if (!dragState.active) {
        rotationState.y = spinBase.y + t * 0.12;
        rotationState.x = spinBase.x + Math.sin(t * 0.22) * 0.06;
      }
      root.rotation.y = rotationState.y;
      root.rotation.x = rotationState.x;
      clouds.rotation.y = t * 0.24;
      earth.rotation.y = rotationState.y;
      flare.scale.setScalar(1.1 + Math.sin(t * 2.2) * 0.06);
      caseRings.forEach((ring, index) => {
        const active = INCIDENTS[index]?.id === selectedIdRef.current;
        ring.scale.setScalar(active ? 0.95 + Math.sin(t * 5.4) * 0.03 : 0.55 + Math.sin(t * 3.2 + index) * 0.02);
        const material = ring.material as THREE.MeshBasicMaterial;
        material.opacity = active ? 0.24 + Math.sin(t * 4.5) * 0.03 : 0.08 + Math.sin(t * 2.8 + index) * 0.02;
      });
      routeLines.forEach(({ line, glow }) => {
        const visible = line.visible;
        const intensity = visible ? 0.72 + Math.sin(t * 3) * 0.08 : 0.08;
        (line.material as THREE.LineBasicMaterial).opacity = intensity;
        (glow.material as THREE.LineBasicMaterial).opacity = visible ? 0.22 + Math.sin(t * 2.6) * 0.04 : 0.02;
      });
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
      window.removeEventListener("pointermove", onPointerMove);
      window.removeEventListener("pointerup", onPointerUp);
      window.removeEventListener("pointerdown", onPointerDown);
      routeGeometries.forEach((geometry) => geometry.dispose());
      renderer.dispose();
      host.removeChild(renderer.domElement);
    };
  }, []);

  return (
    <div className="globe-shell">
      <div ref={hostRef} className="globe-canvas-host" />
      <div className="globe-scanlines" />
      <div className="globe-vignette" />
      <div className="globe-incident-copy">
        <span>ACTIVE CASE</span>
        <strong>{selectedIncident.label}</strong>
        <small>{selectedIncident.lat.toFixed(3)}, {selectedIncident.lon.toFixed(3)}</small>
        <em>{ROUTES[selectedIncident.id]?.length ?? 0} linked locations</em>
      </div>
    </div>
  );
}
