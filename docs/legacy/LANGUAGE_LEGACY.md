# kivai-language
The official grammar and syntax of the Kivai language for intelligent device interaction.

> Legacy terminology note: references to "protocol" or legacy command formats in this document predate the Kivai Platform naming and v1.0 intent schema.

# Kivai Language Reference

Kivai is a simple, universal, human-readable language designed for communicating with intelligent devices — naturally and efficiently.

This repository defines the grammar, structure, syntax, and interaction model of the Kivai language.

---

## 🔤 Purpose

To create a unified way for people to speak to devices — regardless of language, brand, or platform — using a minimal, intuitive, and voice-first structure.

---

## 📐 Sentence Structure

Kivai follows a clean and consistent format:


**Examples:**

- `Kivai turn on the lights`
- `Kivai play music in the kitchen`
- `Kivai set temperature to 72`
- `Kivai open window in bedroom`
- `Kivai mute the TV`

---

## 🧠 Smart Context & Multi-Device Handling

- Only the **closest device**, or the one with **best contextual confidence**, will respond.
- Devices detect **zones** (e.g. kitchen, bedroom) and **roles** (e.g. lights, media).
- Devices can communicate with each other to pass off commands if needed.

---

## 🔄 Alternate Sentence Styles

Kivai also supports variations like:

- `Turn on the lights, Kivai`
- `Lights on, Kivai`
- `Hey Kivai, dim the lights`

All forms trigger the same intent, as long as the **trigger word "Kivai"** is present.

---

## 🌍 Language-Agnostic Design

While Kivai is designed to be spoken in **any native language**, the presence of the word “Kivai” in a sentence marks the command for devices.

**Examples:**

- Spanish: `Kivai enciende la luz`
- French: `Kivai allume la lumière`
- Hindi: `Kivai, light on karo`

---

## 🧱 Modular & Expandable

Kivai is designed to grow:

- Plug in new verbs, objects, and context rules
- Expand to gestures, screen taps, or text input
- Map to APIs via Kivai Protocol (see `kivai-protocol` repo coming soon)

---

## 🚧 Work In Progress

This repo is the foundation for defining:

- ✅ Core grammar & syntax
- ✅ Command structure
- 🔲 Multi-language support rules
- 🔲 Training data examples
- 🔲 NLP API integration strategies

---

## 🙌 Contribute

We invite linguists, developers, designers, and makers to help define how humans and machines speak to one another.

Open an issue. Suggest a command format. Submit ideas. Let’s shape the Kivai language together.

---

## License Status

This repository is archived for historical reference.

The active and official Kivai platform is maintained under the Tech4Life & Beyond organization and licensed under TOIL v1.0.

See:
https://github.com/tech4life-beyond/kivai


---

Tech for Life. Tech for All. Speak Kivai.
