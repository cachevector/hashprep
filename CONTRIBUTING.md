# Contributing to HashPrep

First off – thank you for considering contributing to HashPrep 💜  
Your contributions help make this platform more useful for the ML community!

## How to Contribute

Pull requests are welcome! For major changes, please open an issue first to discuss what you’d like to change.
For new contributors, we suggest starting with Easy tasks.

## Setup Instructions

### Fork and clone the repository
```bash
git clone https://github.com/cachevector/hashprep.git
```

### CLI

```bash
cd /hashprep/cli/
python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt 
```

### Run the CLI

```bash
python hashprep/cli/main.py --help
```

<!-- To keep your fork updated:

```bash
git remote add upstream https://github.com/cachevector/hashprep.git
git fetch upstream
git branch --set-upstream-to=upstream/main main 
```
-->

## Pull Request Guidelines

Don’t worry if you don’t get everything right – we’ll gladly help out.  

### PR Titles  
Follow [Conventional Commits](https://www.conventionalcommits.org/):  

  `feat`: → New feature  
  `fix`: → Bug fix  
  `docs`: → Documentation changes  
  `style`: → Formatting, whitespace, non-functional  
  `refactor`: → Code change without new feature/bug fix  
  `perf`: → Performance improvement  
  `test`: → Adding/correcting tests  
  `build`: → Build system or dependency changes  
  `ci`: → CI/CD configuration  
  `chore`: → Maintenance tasks  
  `revert`: → Reverts a previous commit

  Example: `feat: add outlier detection module`

### PR Content

- Keep PRs small and focused.
- Use clear titles (example: `feat: add CLI command for dataset profiling`).
- Add a short description of _why_ you’re making the change.
- If possible, add tests or examples to help us review faster.

### Good to Know

- It’s fine if you’re new to open source, we’re happy to help you through the process.
- Documentation, bug reports, and testing are just as valuable as code!
- The roadmap is evolving, if you have ideas, bring them up in issues/discussions.

---

_Happy debugging!_
