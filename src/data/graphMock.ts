/**
 * Synthetic offline graph used when the backend is unreachable.
 *
 * A coherent fictional network consistent with the existing mock entities so the
 * frozen UI always renders something meaningful during a demo without the API.
 */
import type { GraphResponse } from "../services/api";

// Coherent synthetic network derived from the existing mock entities.
export const mockGraph: GraphResponse = {
  nodes: [
    { id: "P-2041", type: "PERSON", name: "Person A", properties: { risk: 94, confidence: 96 } },
    { id: "P-7712", type: "PERSON", name: "Person B", properties: { risk: 71, confidence: 88 } },
    { id: "P-0182", type: "PERSON", name: "Person C", properties: { risk: 66, confidence: 84 } },
    { id: "O-1101", type: "ORGANIZATION", name: "Organization Orion", properties: { risk: 89 } },
    { id: "O-2033", type: "ORGANIZATION", name: "Organization Meridian", properties: { risk: 77 } },
    { id: "V-2048", type: "VEHICLE", name: "Vehicle VX-2048", properties: { risk: 58 } },
    { id: "V-1191", type: "VEHICLE", name: "Vehicle VX-1191", properties: { risk: 49 } },
    { id: "N-4821", type: "PHONE", name: "Phone 4821", properties: { risk: 62 } },
    { id: "N-9044", type: "PHONE", name: "Phone 9044", properties: { risk: 40 } },
    { id: "L-3007", type: "LOCATION", name: "Sector 17", properties: { risk: 83 } },
    { id: "L-4002", type: "LOCATION", name: "Dock 4", properties: { risk: 70 } },
    { id: "A-4200", type: "ACCOUNT", name: "Account 4200", properties: { risk: 76 } },
    { id: "A-0182", type: "ACCOUNT", name: "Account 0182", properties: { risk: 69 } },
  ],
  edges: [
    { id: "E-001", source: "P-2041", target: "O-1101", type: "MEMBER_OF", properties: { confidence: 0.92 } },
    { id: "E-002", source: "P-2041", target: "V-2048", type: "OWNS", properties: { confidence: 0.95 } },
    { id: "E-003", source: "P-2041", target: "N-4821", type: "USES", properties: { confidence: 0.94 } },
    { id: "E-004", source: "N-4821", target: "L-3007", type: "USES", properties: { confidence: 0.86 } },
    { id: "E-005", source: "P-2041", target: "A-4200", type: "OWNS", properties: { confidence: 0.9 } },
    { id: "E-006", source: "P-7712", target: "O-2033", type: "MEMBER_OF", properties: { confidence: 0.88 } },
    { id: "E-007", source: "P-7712", target: "V-1191", type: "OWNS", properties: { confidence: 0.91 } },
    { id: "E-008", source: "P-7712", target: "N-9044", type: "USES", properties: { confidence: 0.87 } },
    { id: "E-009", source: "N-9044", target: "L-4002", type: "USES", properties: { confidence: 0.82 } },
    { id: "E-010", source: "A-4200", target: "A-0182", type: "TRANSFERRED_TO", properties: { confidence: 0.97, amount: 2400000 } },
    { id: "E-011", source: "P-2041", target: "P-7712", type: "ASSOCIATED_WITH", properties: { confidence: 0.78 } },
    { id: "E-012", source: "P-0182", target: "O-1101", type: "MEMBER_OF", properties: { confidence: 0.85 } },
    { id: "E-013", source: "P-0182", target: "L-3007", type: "VISITED", properties: { confidence: 0.8 } },
  ],
};

// Influencer ranking (by network centrality/importance) using the mock graph.
export const mockInfluencers = [
  { id: "P-2041", name: "Person A", score: 94.8 },
  { id: "O-1101", name: "Organization Orion", score: 89.2 },
  { id: "P-7712", name: "Person B", score: 81.7 },
  { id: "L-3007", name: "Sector 17", score: 76.2 },
];
