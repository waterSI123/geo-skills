# Gap And Risk Rules

Use rule-based signals with short evidence snippets. Do not overclaim: uncertain wrong-category or wrong-feature cases should be marked `review_required`.

## Content Gap Signals

Allowed signal types:

- `competitor_recommended_client_absent`
- `policy_compliance_gap`
- `proof_asset_gap`
- `unclear_positioning`
- `competitor_maturity_advantage`
- `weak_client_recommendation`

### competitor_recommended_client_absent

Trigger when at least one competitor is recommended or positively described and the client brand is absent.

### policy_compliance_gap

Trigger when the answer references policy, compliance, or brand-guideline needs and the client brand is absent.

Keywords:

```text
brand guidelines
platform policy
ad policy
compliance
creative compliance
copyright
usage rights
```

### proof_asset_gap

Trigger when the answer says buyers need proof assets or references them as selection criteria.

Keywords:

```text
case studies
pricing
integrations
reviews
examples
testimonials
customer stories
benchmarks
demo
```

### unclear_positioning

Trigger when the client brand is mentioned near uncertainty language.

Keywords:

```text
not enough information
unclear
unknown
hard to verify
limited information
not widely documented
```

### competitor_maturity_advantage

Trigger when a competitor is described as more mature, better known, or more suitable.

Keywords:

```text
more established
better known
more mature
widely used
more suitable
stronger option
better fit
```

### weak_client_recommendation

Trigger when the client brand appears but is not recommended and sentiment is not positive.

## Risk Signals

Allowed signal types:

- `negative_brand_mention`
- `insufficient_brand_information`
- `wrong_category_needs_review`
- `wrong_website`
- `wrong_feature_needs_review`
- `brand_existence_uncertain`

### negative_brand_mention

Trigger when negative language appears near the client brand.

### insufficient_brand_information

Trigger when the answer says the client brand lacks enough information, evidence, documentation, or public proof.

### wrong_category_needs_review

Trigger when the client brand is described with category language that has little overlap with the known product or service direction. Mark `review_required: true`.

### wrong_website

Trigger when a website/domain appears near the client brand and it does not match the official client website domain.

### wrong_feature_needs_review

Trigger when the answer attributes off-domain product capabilities to the client brand and known service-direction terms do not support that claim. Mark `review_required: true`.

### brand_existence_uncertain

Trigger when the answer cannot confirm whether the client brand exists or is real.

Keywords:

```text
cannot confirm
can't confirm
does not appear to exist
not sure it exists
hard to verify
not widely documented
no reliable information
```
