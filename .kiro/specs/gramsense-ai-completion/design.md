# GramSense AI Prototype Completion - Design Document

## System Architecture

### High-Level Architecture
```
┌──────────────────────────────────────────────────────────────┐
│                        Internet/Users                         │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│                    AWS EC2 Instance                           │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Nginx (Reverse Proxy)                                 