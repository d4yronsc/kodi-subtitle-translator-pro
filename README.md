# Subtitle Translator Pro (TaMaBin) for Kodi

[![GitHub Release](https://img.shields.io/github/v/release/d4yronsc/kodi-subtitle-translator-pro?label=version)](https://github.com/d4yronsc/kodi-subtitle-translator-pro/releases)
[![License](https://img.shields.io/badge/license-GPL--3.0-green)](LICENSE)

**Professional-quality subtitle translation for Kodi with Netflix broadcast standards.**

Fork of [yeager/kodi-subtitle-translator](https://github.com/yeager/kodi-subtitle-translator) by [Daniel Nylander](https://github.com/yeager), with significant quality and workflow improvements.

## What's New in v1.0.0

### 3-Tier Subtitle Priority System
Instead of translating everything, the addon now follows a smart priority system:

1. **Embedded subtitles** — Uses Spanish (or your target language) subtitles already embedded in the video
2. **Subtitle search** — Searches via your installed subtitle addons (a4ksubtitles, OpenSubtitles, etc.)
3. **Translation** — Translates only as a last resort, saving your API credits

### TaMaBin Professional Translation Quality
- **Netflix subtitle standards**: 42 chars/line max, 2 lines max, 833ms min duration, 7s max duration, 17 CPS reading speed
- **Balanced line wrapping**: Upper line always shorter than or equal to lower line (broadcast standard)
- **HTML tag preservation**: Keeps `<i>`, `<b>`, `<u>` formatting through translation pipeline
- **Spanish latino neutro** post-processing for DeepL: dialogue dashes (—→"- "), opening punctuation (¿¡), classical orthography ("sólo")
- **Full TaMaBin prompt** for Claude/OpenAI: genre-calibrated register, natural dialogue, proper number formatting

### Default Configuration for Spanish
- Default target language: **Spanish** (was Swedish)
- Default translation service: **DeepL Free** (was MyMemory)
- Informal formality automatically applied for Spanish translations

## Installation

1. Download `service.subtitletranslator.tamabin-1.0.0.zip` from [Releases](https://github.com/d4yronsc/kodi-subtitle-translator-pro/releases)
2. In Kodi: **Settings → Add-ons → Install from zip file**
3. Select the downloaded ZIP
4. Configure: **Add-ons → My add-ons → Services → Subtitle Translator Pro → Configure**

## Configuration

### Subtitle Priority (new settings)
| Setting | Description | Default |
|---------|-------------|---------|
| Search for subtitles | Enable/disable searching via installed subtitle addons | On |
| Search wait time | How long to wait for subtitle search results | 15s |
| Priority mode | Embedded→Search→Translate / Embedded→Translate / Search only | Embedded→Search→Translate |

### Translation Services

| Service | API Key | Free Tier | TaMaBin Quality |
|---------|:---:|:---:|:---:|
| **DeepL Free** (default) | ✅ | 500k chars/month | ✅ Post-processing |
| DeepL Pro | ✅ | Unlimited | ✅ Post-processing |
| **Claude AI** (Anthropic) | ✅ | Pay-per-use | ✅ Full TaMaBin prompt |
| **OpenAI GPT** | ✅ | Pay-per-use | ✅ Full TaMaBin prompt |
| Lingva | ❌ | Unlimited | Basic |
| Google Translate | ✅ | Limited | Basic |
| Microsoft Translator | ✅ | 2M chars/month | Basic |
| LibreTranslate | ✅ | Self-hosted | Basic |
| Argos Translate | ❌ | Offline | Basic |
| MyMemory | ❌ | 5k chars/day | Basic |

> **Recommended**: DeepL Free gives you 500,000 characters/month for free — more than enough for casual viewing. For best quality, use Claude AI with the full TaMaBin professional prompt.

## Requirements

- Kodi 19 (Matrix) or later
- For subtitle search priority: Install a subtitle addon (a4ksubtitles, OpenSubtitles, etc.)
- For DeepL: Free API key from [deepl.com/pro-api](https://www.deepl.com/pro-api)
- For Claude/OpenAI: API key from respective provider

## Platforms

- Windows, macOS, Linux
- Android TV (Nvidia Shield, Fire TV)
- Network sources: SMB, NFS, local files

## Credits

- **Original addon**: [yeager/kodi-subtitle-translator](https://github.com/yeager/kodi-subtitle-translator) by [Daniel Nylander](https://danielnylander.se)
- **TaMaBin Pro improvements**: [d4yronsc](https://github.com/d4yronsc)
- Translation quality standards based on Netflix Timed Text Style Guide

## License

GPL-3.0-or-later (same as original)
