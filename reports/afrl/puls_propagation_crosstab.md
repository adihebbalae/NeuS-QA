# PULS spec faithfulness → downstream propagation (test, n=3000)

- Faithful specs: **2031** (67.7%)
- FOI=[-1] overall: **72.8%**
- Sub7b ≠ baseline overall: **25.0%**

### spec_faithful × foi_minus1

| spec_faithful | FOI=[-1] | FOI ok | row_n | rate(FOI=[-1]|row) |
|---|---:|---:|---:|---:|
| faithful | 1362 | 669 | 2031 | 67.1% |
| unfaithful | 821 | 148 | 969 | 84.7% |

P(FOI=[-1] | unfaithful) = **84.7%**; P(FOI=[-1] | faithful) = **67.1%**; lift = **1.26×**.

### spec_faithful × ours_ne_vanilla

| spec_faithful | ours≠vanilla | ours=vanilla | row_n | rate(ours≠vanilla|row) |
|---|---:|---:|---:|---:|
| faithful | 535 | 1496 | 2031 | 26.3% |
| unfaithful | 214 | 755 | 969 | 22.1% |

P(ours≠vanilla | unfaithful) = **22.1%**; P(ours≠vanilla | faithful) = **26.3%**; lift = **0.84×**.

Unfaithful PULS specs associate with higher FOI=[-1] (NSVS bypass) rates, showing operator mismatch propagates to downstream interval retrieval failure.
