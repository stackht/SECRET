import { Entity } from "../types";

export const dashboardMetrics = [
  { label: "Active Investigations", value: 128 },
  { label: "Entities Monitored", value: 24891 },
  { label: "Relationships Mapped", value: 182430 },
  { label: "High-Risk Alerts", value: 17 }
];

export const entities: Entity[] = [
  { id: "P-2041", name: "Person A", type: "Person", risk: 94, confidence: 96, relationships: 18, lastActivity: "14:32", aliases: ["A. Khan", "Alpha"], phones: ["+91-XXX-1842"], vehicles: ["VX-2048"], locations: ["Sector 17"], organizations: ["Orion"], },
  { id: "P-7712", name: "Person B", type: "Person", risk: 71, confidence: 88, relationships: 12, lastActivity: "13:18", aliases: ["B. Malik"], phones: ["+91-XXX-7712"], vehicles: ["VX-1191"], locations: ["Dock 4"], organizations: ["Meridian"], },
  { id: "O-1101", name: "Organization Orion", type: "Organization", risk: 89, confidence: 92, relationships: 44, lastActivity: "14:27", aliases: ["Orion Group"], locations: ["Sector 17"], organizations: ["Meridian"], },
  { id: "V-2048", name: "Vehicle VX-2048", type: "Vehicle", risk: 58, confidence: 84, relationships: 7, lastActivity: "11:46", aliases: ["Black sedan"], locations: ["Sector 9"], },
  { id: "L-3007", name: "Sector 17", type: "Location", risk: 83, confidence: 90, relationships: 21, lastActivity: "10:03", aliases: ["S-17"], organizations: ["Orion"], },
  { id: "A-4200", name: "Account 4200", type: "Account", risk: 76, confidence: 87, relationships: 9, lastActivity: "09:17", aliases: ["Ledger 4200"], organizations: ["Meridian"], }
];

export const alerts = [
  { severity: "CRITICAL", title: "Rapid expansion of entity network", time: "14:32:08" },
  { severity: "HIGH", title: "Unusual transaction pattern", time: "14:31:44" },
  { severity: "MEDIUM", title: "New communication cluster identified", time: "14:29:17" },
  { severity: "LOW", title: "Entity risk score updated", time: "14:27:03" }
];

export const feed = [
  "New relationship discovered",
  "Suspicious transaction detected",
  "New communication cluster identified",
  "Entity risk score updated"
];
