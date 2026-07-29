# Publishing the project

Three options. Vercel is the recommended path for production deployment.
Netlify Drop takes about thirty seconds and requires no account.
GitHub Pages takes about ten minutes and gives you a permanent repository you
can cite in a report, which is the better choice for an assessed project.

---

---

## Option C. Vercel, recommended for production

Vercel is the recommended deployment platform. It supports the project's
`vercel.json` configuration out of the box.

### One-click deploy (recommended)

1. Push the repo to GitHub
2. Go to [vercel.com/new](https://vercel.com/new)
3. Import the `panavkbysani2011-jpg/finch-heatsink` repository
4. Vercel automatically detects the `vercel.json` config
5. Click **Deploy**

The `vercel.json` file in this repo is preconfigured:

```json
{
  "outputDirectory": "dist",
  "buildCommand": "npm run build",
  "devCommand": "npm run dev",
  "installCommand": "npm install",
  "framework": null
}
```

### What happens during build

1. Vercel runs `npm install` to install dependencies
2. Vercel runs `npm run build`, which copies `flinch/*` into the `dist/` directory
3. Vercel serves the files from `dist/` at your deployment URL

The landing page (`flinch/index.html`, the project overview) is served at the
root URL. The interactive tool is at `/tool.html`. The technical report is at
`/findings.html`.

### Quick deploy links

- [Import to Vercel](https://vercel.com/new)
- [Vercel dashboard](https://vercel.com/dashboard)

---

## Option A. Netlify Drop, fastest

1. Open [app.netlify.com/drop](https://app.netlify.com/drop)
2. Drag the entire `finch` folder onto the page
3. A live URL appears within about thirty seconds

The URL is random, for example `heuristic-tesla-4f2a1c.netlify.app`. Free
accounts allow renaming it to something like `finch-heatsink.netlify.app`.

Note: the landing page must be `index.html` for the site root to work. Since
the tool is currently `index.html` and the overview is `home.html`, either
rename the files before uploading or share the direct link to `home.html`.

---

## Option B. GitHub Pages, recommended

### Step 1, create the account and repository

1. Sign up at [github.com](https://github.com) if you have not already
2. Click the **+** icon, top right, then **New repository**
3. Repository name: `finch-heatsink`
4. Set it to **Public**. GitHub Pages requires this on free accounts
5. Do **not** tick "Add a README file"
6. Click **Create repository**

### Step 2, prepare the folder

GitHub Pages serves whatever file is named `index.html` at the root. The
overview page should therefore be the landing page.

Rename as follows before uploading:

| Current name | New name |
|---|---|
| `home.html` | `index.html` |
| `index.html` | `tool.html` |
| `findings.html` | `findings.html`, unchanged |

The internal navigation links must be updated to match. Run this from inside
the `finch` folder:

```bash
cd finch
mv index.html tool.html
mv home.html index.html
sed -i 's|href="index.html"|href="tool.html"|g; s|href="home.html"|href="index.html"|g' *.html
```

On Windows without a Unix shell, rename the two files manually and use find
and replace in a text editor: change `href="index.html"` to `href="tool.html"`
first, then `href="home.html"` to `href="index.html"`.

### Step 3, upload

**Browser method, no software required**

1. On the empty repository page click **uploading an existing file**
2. Drag in `index.html`, `tool.html`, `findings.html` and `style.css`
3. Commit message: `Initial commit`
4. Click **Commit changes**

**Command line method**

```bash
cd finch
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/finch-heatsink.git
git push -u origin main
```

Replace `YOUR-USERNAME` with your GitHub username. GitHub will ask you to
authenticate; use a personal access token rather than a password, generated
under Settings, Developer settings, Personal access tokens.

### Step 4, enable Pages

1. In the repository, click **Settings**
2. Select **Pages** in the left sidebar
3. Under **Source**, choose **Deploy from a branch**
4. Branch: `main`, folder: `/ (root)`
5. Click **Save**

The site appears at:

```
https://YOUR-USERNAME.github.io/finch-heatsink/
```

The first build takes one to two minutes. A green tick beside the commit
indicates the deployment has completed.

### Step 5, verify

Open the URL and confirm:

- The overview page loads with correct fonts
- Navigation between all three pages works
- The tool runs and the temperature falls when Evolve is pressed
- The page displays correctly on a phone

---

## Including the analysis code

For an assessed project it is worth publishing the Python alongside the site,
as evidence that results are reproducible.

Recommended repository structure:

```
finch-heatsink/
  index.html            overview
  tool.html             interactive tool
  findings.html         technical report
  style.css
  README.md
  sim/                  analysis scripts and data
  figures/              generated figures
```

Upload `sim/` and `figures/` as additional folders. GitHub Pages ignores them
when serving the site, but they remain visible in the repository.

---

## README.md

Create this file at the repository root. It is the first thing anyone sees.

```markdown
# FINCH

Evolutionary optimisation of heat sink geometry against a validated
two-dimensional thermal model.

**Live site:** https://YOUR-USERNAME.github.io/finch-heatsink/

## Summary

Conventional heat sinks use straight radial fins, a geometry selected for
extrusion economy rather than demonstrated thermal optimality. This project
applies population-based stochastic search to generate heat sink geometry
directly from physics, and evaluates it against a controlled conventional
reference under identical material allocation.

Optimised geometry reduces peak temperature by 3 to 20 percent depending on
the thermal regime, with the greatest benefit in the intermediate conduction
regime where heat reaches a useful but incomplete fraction of the structure.

## Model

Two-dimensional steady-state conduction with channel-limited convection and
linearised surface radiation. Validated against the analytical fin equation to
within 0.001 percent, with second-order spatial convergence confirmed.
Independently reimplemented in Python and JavaScript, agreeing to 0.0002 °C.

## Reproducing the results

```bash
cd sim
python3 validate2.py       # validation suite, 14 assertions
python3 regime2.py         # thermal regime sweep
python3 airflow_test.py    # convective model sensitivity
python3 mapelites_test.py  # quality diversity comparison
python3 test_site.py       # verifies all published values
```

Requires numpy, scipy and matplotlib.

## References

- Mouret and Clune (2015), Illuminating search spaces by mapping elites
- Bar-Cohen and Rohsenow (1984), Thermally optimum spacing of vertical,
  natural convection cooled, parallel plates
- Incropera and DeWitt, Fundamentals of Heat and Mass Transfer
```

---

## Updating the site later

**Browser:** open the file in the repository, click the pencil icon, edit,
commit. The site rebuilds automatically within about a minute.

**Command line:**

```bash
git add .
git commit -m "Describe the change"
git push
```

---

## Common problems

**The site shows a 404.** Pages was not enabled, or the branch is wrong.
Recheck Settings, Pages. Allow two minutes after the first commit.

**The site loads but has no styling.** `style.css` was not uploaded, or the
filename case does not match. GitHub Pages is case sensitive, unlike Windows.

**Fonts do not load.** The page falls back to system fonts automatically and
remains fully readable. This is expected offline.

**Navigation links break.** The rename in Step 2 was applied to the files but
not to the `href` attributes inside them. Search each file for
`href="home.html"` and correct it.

---

## Citing it in a report

> Interactive tool and technical report available at
> https://YOUR-USERNAME.github.io/finch-heatsink/
> Source code and analysis scripts at
> https://github.com/YOUR-USERNAME/finch-heatsink
