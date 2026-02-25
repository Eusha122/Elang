# Elang

<p align="center">
  <img src="E.svg" width="110" alt="Elang Logo"/>
</p>

<p align="center">
  <strong>A lightweight, beginner-focused programming language.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-0.1.0-blue?style=flat-square" />
  <img src="https://img.shields.io/badge/runtime-standalone-green?style=flat-square" />
  <img src="https://img.shields.io/badge/license-MIT-orange?style=flat-square" />
  <img src="https://img.shields.io/badge/extension-.elang-purple?style=flat-square" />
</p>

---

## Overview

**Elang** is a lightweight interpreted programming language focused on clarity and simplicity. It features a clean syntax, first-class functions, built-in modules, and a standalone Windows runtime.

This is the initial public release (**v0.1.0**). Elang is currently focused on experimentation in language design and runtime architecture.

---

## Installation (Windows)

1. Download the latest release from the **Releases** section.
2. Run `ElangSetup.exe`.
3. After installation, verify by running:
   ```bash
   elang hello.elang
   ```

**The installer can optionally:**
- ✅ Add Elang to your system **PATH**
- ✅ Associate **.elang** files (double-click to run)
- ✅ Install the **VS Code extension** automatically

---

## Quick Example

```eusha
say("Hello, World!").newl
```

---

## Language Features

### Variables
```eusha
name = "Eusha"
age = 16
active = true
```

### String Interpolation
```eusha
say("Hello {name}, you are {age} years old!").newl
say("2 + 3 = {2 + 3}").newl
```

### Functions
```eusha
fn greet(name) {
    say("Hello {name}!").newl
}
```

### Lambdas
```eusha
nums = [1, 2, 3, 4, 5]
evens = nums.filter(x => x % 2 == 0)
```

### Arrays
```eusha
nums = [3, 1, 4, 1, 5]
nums.sort()
say(nums.sum()).newl
```

### Objects
```eusha
person = {name: "Eusha", age: 16}
say(person.name).newl
```

### Control Flow
```eusha
if age >= 18 {
    say("Adult").newl
} else {
    say("Minor").newl
}

for (i in 1..5) {
    say(i).space
}

while x < 10 {
    x += 1
}
```

### Modules
```eusha
use math
say(math.sqrt(25)).newl

use random
say(random.randint(1, 10)).newl
```

---

## VS Code Support

The repository includes a VS Code extension providing:
- ✨ Syntax highlighting
- ▶️ Run command integration (Play button)
- 📥 Automatic bracket completion

**Manual Install:**
Install from VSIX → `elang-language-0.1.0.vsix`

---

## Built-in Modules

| Module  | Description |
|---------|-------------|
| `math`  | Basic mathematical functions and constants |
| `random`| Random number generation utilities |

---

## Repository Structure

- `elang/`: Interpreter source code
- `eusha-language/`: VS Code extension source
- `examples/`: Example Elang programs
- `ElangSetup.iss`: Windows installer script (Inno Setup)

---

## Project Status

Elang is an early-stage language implementation under active development. The syntax and APIs may evolve over time.

---

## License

Distributed under the **MIT License**. See `LICENSE` for more information.

---

<p align="center">
  <em>Elang is developed and maintained by Eusha</em><br/>
  <strong>"Programming should be fun."</strong>
</p>
