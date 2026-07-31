# Landing Page Specification

Last reviewed: 2026-07-31  
Status: Authoritative public-site content and structure specification

## 1. Purpose

Define the public landing page for **The Daily Roast AI** at `thedailyroast.online`.

The landing page must explain the product clearly, establish trust, avoid financial hype, and direct users to the demo or sign-in experience.

## 2. Primary Audience

- retail investors who want understandable market research;
- technically minded users evaluating AI-assisted analysis;
- reviewers and early testers of the cloud demo;
- future professional users comparing research workflows.

## 3. Primary Message

**The Daily Roast AI**  
**Evidence-Driven Market Intelligence**

Supporting message:

> Understand market evidence, test ideas, inspect risk, and simulate decisions before real capital is considered.

## 4. Primary Calls to Action

Primary CTA:

- Open the Demo

Secondary CTA:

- Explore the Methodology

Authenticated returning users may see:

- Sign In

Do not use urgency, scarcity, profit promises, or deposit-oriented CTAs.

## 5. Page Structure

### 5.1 Header

- wordmark;
- Product;
- Methodology;
- Security;
- Documentation;
- Sign In;
- Open the Demo.

### 5.2 Hero

Required content:

- official product name;
- official tagline;
- one-sentence value proposition;
- primary and secondary CTA;
- product screenshot or interface illustration;
- explicit label that the initial version uses paper trading.

### 5.3 Problem Section

Explain common research problems:

- fragmented data;
- unexplained AI recommendations;
- hidden assumptions;
- weak risk context;
- backtests that omit realistic costs;
- decisions that cannot be reproduced.

### 5.4 Product Pillars

Use five pillars:

1. Market Evidence
2. Explainable AI
3. Deterministic Risk
4. Reproducible Testing
5. Auditable Simulation

### 5.5 How It Works

```text
Market data
  -> validation
  -> deterministic features
  -> Gemini analysis
  -> strategy
  -> risk
  -> paper simulation
  -> audit and reporting
```

The section must state that Gemini is advisory and cannot place orders.

### 5.6 Today's Roast Preview

Show a representative, clearly labeled demo card containing:

- symbol;
- market regime;
- evidence summary;
- AI confidence;
- contradictions;
- risk status;
- simulated action or HOLD.

Sample data must never be presented as current real advice.

### 5.7 Safety and Transparency

Cover:

- paper trading only in MVP;
- deterministic risk controls;
- complete decision lineage;
- no profit guarantees;
- no custody or withdrawals;
- no private Binance trading credentials.

### 5.8 Backtesting and Portfolio

Explain realistic fees, spread, slippage, benchmark comparison, drawdown, and ledger reconciliation.

### 5.9 Built for Inspection

Highlight:

- evidence references;
- model and prompt versions;
- risk reason codes;
- audit trail;
- reproducible configuration;
- exports.

### 5.10 Deployment and Privacy

Explain only what is accurate for the active release. Do not publish sensitive architecture details or imply stronger privacy guarantees than implemented.

### 5.11 FAQ

Minimum questions:

- Does The Daily Roast AI provide financial advice?
- Does it trade real money?
- Can Gemini place orders?
- What is paper trading?
- What data does the system use?
- How are backtests made realistic?
- Is profit guaranteed?
- Which markets are supported?
- How is user data protected?

### 5.12 Final CTA

- Open the Demo
- Read the Methodology

### 5.13 Footer

- Product;
- Documentation;
- Security;
- Privacy;
- Terms;
- GitHub if public;
- status page;
- disclaimer.

## 6. SEO

Recommended title:

`The Daily Roast AI — Evidence-Driven Market Intelligence`

Recommended description:

`Inspect market evidence, Gemini-assisted research, deterministic risk controls, backtests, and paper-trading simulations with complete decision lineage.`

Use structured metadata appropriate to a software product. Do not use misleading investment-performance keywords.

## 7. Trust Requirements

- Every screenshot identifies environment and simulation state.
- Claims must be supported by implemented features.
- Future capabilities are labeled as planned.
- No invented customer testimonials.
- No fabricated performance statistics.
- Security claims require implemented evidence.
- Pricing is omitted until a real pricing policy exists.

## 8. Accessibility and Performance

- semantic heading structure;
- keyboard-accessible navigation;
- visible focus states;
- optimized responsive images;
- meaningful alt text;
- reduced-motion support;
- acceptable contrast;
- performance budget for initial load;
- no autoplay media.

## 9. Analytics

Analytics are optional and require privacy review.

If enabled:

- collect minimal event data;
- avoid financial and sensitive identifiers;
- document consent and retention where required;
- never send secrets, portfolio details, or Gemini prompts.

## 10. Definition of Done

The landing page is complete when:

- copy matches brand and product requirements;
- demo and sign-in links work;
- all claims are implementation-accurate;
- paper-trading scope is explicit;
- accessibility checks pass;
- mobile and desktop layouts are verified;
- metadata is configured;
- no secret or private environment value appears in the build;
- legal and privacy links exist before public production launch.

## 11. Related Documents

- `BRAND_GUIDELINES.md`
- `PRODUCT_VISION.md`
- `MISSION_AND_VALUES.md`
- `DESIGN_SYSTEM.md`
- `UI_UX_GUIDELINES.md`
- `SECURITY.md`
