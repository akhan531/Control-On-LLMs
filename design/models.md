# Model roster

Seven configurations across four model families were run over every stimulus.
A configuration is a model paired with a reasoning setting and token budget; the
`-high` member of a pair raises both. All calls went through the OpenRouter API,
five draws per stimulus (seeds 1--5), with no system prompt and strict decoding
against the response schema.

The **gate score** is the draw-weighted mean `s1` on the printed-negatives
(`FULL`) condition, the competence gate described in the paper. Five
configurations clear the gate (`s1 < 1.0`); the two below the rule are excluded
from all reported results.

| alias | model slug | reasoning | max_tokens | temp. | weights | gate s1 |
|-------|-----------|-----------|-----------:|-------|---------|--------:|
| `sol-hi`   | `openai/gpt-5.6-sol`               | effort high | 12000 | --  | closed | 0.200 |
| `sol-no`   | `openai/gpt-5.6-sol`               | effort none | 800   | --  | closed | 0.421 |
| `glm-hi`   | `z-ai/glm-5.2`                     | enabled     | 16000 | 0.7 | open   | 0.457 |
| `dsk-hi`   | `deepseek/deepseek-v4-flash-0731` | enabled     | 16000 | 0.7 | open   | 0.752 |
| `glm`      | `z-ai/glm-5.2`                    | disabled    | 800   | 0.7 | open   | 0.764 |
| --- gate rule: admit above, exclude below --- | | | | | | |
| `deepseek` | `deepseek/deepseek-v4-flash-0731` | disabled    | 800   | 0.7 | open   | 1.609 |
| `llama`    | `meta-llama/llama-3.3-70b-instruct` | none      | 400   | 0.7 | open   | 1.800 |

Notes:

- `openai/gpt-5.6-sol` does not accept a temperature, so the two `sol`
  configurations vary by seed alone.
- Token budgets are per configuration; reasoning tokens draw from the same
  budget, which is why the `-high` configurations carry the larger `max_tokens`.
- `weights` records whether the provider distributes the model's weights; it is
  the provider's status, not a license grant. The repository records the model
  slugs above, not their terms of use.
- The exact reasoning/budget pairing and the `gate s1` column reproduce from the
  draw records under `results/` via the figure generators in `paper/figures/`.
