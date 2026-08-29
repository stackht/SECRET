export type Section =
  | "login"
  | "command-center"
  | "investigations"
  | "case-intake"
  | "network"
  | "entities"
  | "timeline"
  | "locations"
  | "transactions"
  | "communications"
  | "alerts"
  | "reports"
  | "settings"
  | "assistant"
  | "simulation"
  | "audit";

export type EntityType = "Person" | "Organization" | "Vehicle" | "Phone" | "Location" | "Account";

export type Entity = {
  id: string;
  name: string;
  type: EntityType;
  risk: number;
  confidence: number;
  relationships: number;
  lastActivity: string;
  aliases: string[];
  phones?: string[];
  vehicles?: string[];
  locations?: string[];
  organizations?: string[];
};
