# ADR-0002: Control Plane and Command Envelope

Status: proposed

## Decision

The Control Plane owns identity, tenant/matter scope, conflicts, ethical walls,
policy, approvals, revocations, budgets, commands, receipts, incidents, and
legal holds. All consequential actions use a typed command envelope and durable
receipt state machine.

## Rejected alternative

Allowing agents or connectors to execute directly from a generic CRUD/API route.

## Consequence

Analysis remains automatable; binding or externally consequential actions require
human/policy authorization and independent external reconciliation.
