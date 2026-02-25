<p align="center">
  <img src="icon.png" width="120" alt="Elang Logo"/>
</p>

<h1 align="center">Elang</h1>

<p align="center">
  <strong>A modern, beginner-friendly programming language</strong><br/>
  Fast to learn. Easy to read. Beautiful to write.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-3.0-blue?style=flat-square" alt="Version"/>
  <img src="https://img.shields.io/badge/python-3.8+-green?style=flat-square" alt="Python"/>
  <img src="https://img.shields.io/badge/license-MIT-orange?style=flat-square" alt="License"/>
  <img src="https://img.shields.io/badge/file_ext-.elang-purple?style=flat-square" alt="Extension"/>
</p>

---

## ⚡ Quick Start

```bash
# Run a file
python elang/elang.py hello.elang

# Or use the REPL
python elang/elang.py
```

## 🎯 Hello, World!

```eusha
say("Hello, World!").newl
```

## ✨ Feature Showcase

### Variables & Types
```eusha
name = "Eusha"
age = 16
pi = 3.14
active = true
```

### String Interpolation
```eusha
say("Hello {name}, you are {age} years old!").newl
say("Result: {2 + 3 * 4}").newl
```

### Functions & Closures
```eusha
fn greet(name) {
    say("Hello {name}!").newl
}

fn make_adder(n) {
    return x => x + n
}

add5 = make_adder(5)
say(add5(10)).newl   $$ 15
```

### Lambdas
```eusha
nums = [1, 2, 3, 4, 5, 6]
evens = nums.filter(x => x % 2 == 0)
doubled = nums.map(x => x * 2)
```

### Arrays
```eusha
fruits = ["apple", "banana", "cherry"]
fruits.push("date")
say(fruits.length()).newl    $$ 4
say(fruits[0]).newl          $$ apple

nums = [3, 1, 4, 1, 5]
nums.sort()
say(nums.sum()).newl         $$ 14
```

### Objects
```eusha
person = {name: "Eusha", age: 16, lang: "Elang"}
say(person.name).newl
say(person.keys()).newl      $$ [name, age, lang]
say(person.has("age")).newl  $$ true
```

### Control Flow
```eusha
$$ If / Else
if age >= 18 {
    say("Adult").newl
} else {
    say("Minor").newl
}

$$ For Loops (range)
for (i in 1..5) {
    say(i).space
}

$$ For Each
for (fruit in fruits) {
    say(fruit).newl
}

$$ While
x = 0
while x < 10 {
    x += 1
}

$$ Break & Continue
for (i in 1..10) {
    if i == 5 { break }
    if i % 2 == 0 { continue }
    say(i).space
}
```

### Modules
```eusha
use math
say(math.sqrt(25)).newl     $$ 5.0
say(math.pi).newl           $$ 3.14159...

use random
say(random.randint(1, 100)).newl
say(random.choice(["a", "b", "c"])).newl
```

### String Methods
```eusha
msg = "  Hello World  "
say(msg.trim()).newl          $$ "Hello World"
say(msg.upper()).newl         $$ "  HELLO WORLD  "
say(msg.contains("World")).newl  $$ true
say(msg.split(" ")).newl      $$ list of words
```

### User Input
```eusha
name = take("What's your name? ")
say("Hello {name}!").newl

$$ Take a list of numbers
input = take("Enter numbers: ")
nums = input.split().map(x => x.to_int())
say("Sum: {nums.sum()}").newl
```

### Multi-arg Print
```eusha
say("Name:", name, "Age:", age).newl
```

### Help System
```eusha
help()          $$ list all topics
help("for")     $$ show docs for 'for' loops
```

## 🎨 Syntax Highlighting

Install the **Eusha Language** VS Code extension from the `eusha-language/` folder:

```bash
# From VS Code
# 1. Open Extensions sidebar
# 2. Click "..." menu → "Install from VSIX..."
# 3. Or copy eusha-language/ to ~/.vscode/extensions/eusha-language
```

## 🛠 Built-in Modules

| Module   | Functions |
|----------|-----------|
| `math`   | `sqrt`, `abs`, `floor`, `ceil`, `round`, `pow`, `sin`, `cos`, `tan`, `log`, `pi`, `e` |
| `random` | `randint`, `random`, `choice`, `shuffle`, `uniform` |

## 📁 Project Structure

```
elang/
├── elang.py          # CLI runner & REPL
├── lexer.py          # Tokenizer
├── parser.py         # AST parser
├── evaluator.py      # Tree-walk interpreter
├── nodes.py          # AST node definitions
eusha-language/       # VS Code extension
├── package.json
├── language-configuration.json
└── syntaxes/
    └── eusha.tmLanguage.json
examples/
├── hello.elang
├── test_all.elang
└── test_v3.elang
```

## 📜 Language Reference

| Feature | Syntax |
|---------|--------|
| Variables | `x = 10` |
| Strings | `"hello"` or `'hello'` |
| Interpolation | `"value is {expr}"` |
| Arrays | `[1, 2, 3]` |
| Objects | `{key: value}` |
| Functions | `fn name(params) { body }` |
| Lambdas | `x => expr` or `(x, y) => expr` |
| If/Else | `if cond { } else { }` |
| For Range | `for (i in 1..10) { }` |
| For Each | `for (x in list) { }` |
| While | `while cond { }` |
| Print | `say(expr).newl` |
| Input | `take("prompt")` |
| Module | `use math` |
| Comments | `$$ comment` |
| Compound | `+=`, `-=`, `*=`, `/=` |

---

<p align="center">
  Made with ❤️ by Eusha<br/>
  <em>File extension: <code>.elang</code></em>
</p>
