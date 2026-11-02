# Clean Architecture

This document describes the completely clean architecture for the AI Text-to-3D House beta.

## Project Goal
To build a clean, deterministic, deterministic generative house system. 

## No Database
**IMPORTANT:** There is NO database in this beta. Persistence mechanisms like SQL, SQLite, PostgreSQL, ORMs, and database services are explicitly excluded from this clean foundation. Design persistence can be added in a later phase.

## Architecture Flow

The pipeline operates in a strictly forward direction.

```
USER PROMPT
    ↓
REQUIREMENT PARSER
    ↓
CANONICAL HOUSE MODEL
    ↓
LAYOUT ENGINE
    ↓
VALIDATION
    ↓
  ┌───────┴───────┐
  ↓               ↓
2D PLAN          3D HOUSE
                    ↓
               SAVE DESIGN
```

## Canonical House Model
The **Canonical House Model** is the single source of truth for both 2D and 3D generation. Neither 2D nor 3D rendering engines are allowed to make independent room positioning or architectural layout decisions. They strictly consume the deterministic layout provided by the Layout Engine.
