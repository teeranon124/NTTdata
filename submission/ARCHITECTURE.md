# AutoProcure.AI — AWS Architecture Diagram

> Render this Mermaid diagram (GitHub / VS Code Mermaid preview / mermaid.live) and
> export to PNG for the presentation PDF.

```mermaid
flowchart TB
    subgraph PLANT["5 โรงงาน (ชลบุรี / ระยอง / อยุธยา)"]
        PR["2,489 Purchase Requisitions<br/>(MRO Tail-Spend)"]
    end

    subgraph AWS["AWS Cloud (us-east-1)"]
        subgraph COMPUTE["Serverless Compute (Pay-as-you-go)"]
            ECS["AWS App Runner / ECS Fargate<br/>Flask + Gunicorn (gthread)<br/>Docker image on Amazon ECR"]
        end

        subgraph AGENTS["Multi-Agent Orchestrator"]
            RT["1. Router Agent<br/>Amazon Nova Micro (FAST)<br/>intent + 5 commercial terms"]
            CP["2. Compliance Guardrail<br/>Bedrock Guardrails + rules"]
            MI["3. Market Intelligence<br/>Thai MRO Index + BATNA"]
            NG["4. Strategic Negotiator<br/>Amazon Nova Pro (STRONG)<br/>Thai negotiation + Game Theory"]
            AB["5. Central Arbitrator<br/>TCO Score + BAFO Ranking"]
        end

        GW["Dynamic Model Gateway<br/>(routes by task complexity)"]
        BR["Amazon Bedrock<br/>Converse API"]
        SES["Amazon SES<br/>RFQ Magic Link invites"]
        RDS["Amazon RDS PostgreSQL<br/>Deals / Vendors / Sessions<br/>MessageLog / AuditTrail"]
        SM["AWS Secrets Manager"]
        CW["Amazon CloudWatch"]
    end

    subgraph USERS["Users"]
        BUY["Buyer Dashboard<br/>(SSE real-time cockpit)"]
        SUP["Supplier Portal<br/>(Magic Link, token-secured)"]
        CPO["CPO — HITL Sign-off"]
    end

    SAP["SAP S/4HANA<br/>BAPI_PO_CREATE1"]

    PR -->|aggregate to 61 strategic deals| ECS
    ECS --> GW
    GW --> RT & NG
    RT --> BR
    NG --> BR
    ECS --> CP & MI & AB
    ECS --> SES
    ECS --> RDS
    ECS -.secrets.-> SM
    ECS -.logs.-> CW
    SES -->|RFQ invite| SUP
    SUP -->|negotiate| ECS
    ECS -->|SSE live updates| BUY
    BUY --> CPO
    CPO -->|approve to PO created| SAP
```

## AWS Services Used
| Service | Purpose |
| :--- | :--- |
| Amazon Bedrock (Converse API) | LLM inference — Nova Micro (router) + Nova Pro (negotiator) |
| Amazon Bedrock Guardrails | Prompt-injection / content policy filtering |
| AWS App Runner / ECS Fargate | Serverless container runtime (pay-as-you-go) |
| Amazon ECR | Container image registry |
| Amazon RDS (PostgreSQL) | Relational store: deals, vendors, sessions, audit trail |
| Amazon SES | RFQ Magic Link email invitations |
| AWS Secrets Manager | Secrets (DB creds, keys) |
| Amazon CloudWatch | Logs & metrics |
