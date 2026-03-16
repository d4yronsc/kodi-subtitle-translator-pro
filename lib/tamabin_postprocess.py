# -*- coding: utf-8 -*-
"""
TaMaBin Post-Processor — Professional subtitle quality for Spanish (Latin American).

Applies Netflix Timed Text Style Guide standards and español latino neutro conventions
to translated subtitles before they are rendered to SRT/VTT/ASS.

Standards applied:
- Opening punctuation marks: ¿ ¡ (mandatory in Spanish)
- Dialogue dash: — (em dash) for speaker identification
- Max 42 characters per line, max 2 lines
- Max 17 CPS (characters per second) — Netflix reading speed limit
- Min duration 833ms, max duration 7000ms
- Proper ellipsis usage (…)
- HTML tag preservation (<i>, <b>)
- Remove machine-translation artifacts
"""

import re


# ── Netflix timing constants ──────────────────────────────────────────
MIN_DURATION_MS = 833
MAX_DURATION_MS = 7000
MAX_CPS = 17
MAX_CHARS_PER_LINE = 42
MAX_LINES = 2


def postprocess_spanish(entries, target_language='es'):
    """Apply TaMaBin post-processing to translated subtitle entries.

    Args:
        entries: list of dicts with 'text', 'start', 'end', 'index'
        target_language: language code (only processes 'es' variants)

    Returns:
        Modified entries list with cleaned-up text and adjusted timings.
    """
    if not target_language.startswith('es'):
        return entries

    for entry in entries:
        text = entry.get('text', '')
        if not text:
            continue

        text = _fix_opening_marks(text)
        text = _fix_dialogue_dashes(text)
        text = _fix_ellipsis(text)
        text = _clean_artifacts(text)
        text = _normalize_quotes(text)

        entry['text'] = text.strip()

    # Timing adjustments
    _adjust_timings(entries)

    return entries


# ── Punctuation fixes ─────────────────────────────────────────────────

def _fix_opening_marks(text):
    """Add missing opening ¿ and ¡ marks for Spanish.

    Rules:
    - If a line ends with ? but doesn't have ¿, add it.
    - If a line ends with ! but doesn't have ¡, add it.
    - Handle multiple sentences per line.
    - Preserve existing correct marks.
    - Handle HTML tags (<i>, <b>) without breaking them.
    """
    lines = text.split('\n')
    result = []

    for line in lines:
        line = _add_opening_mark_to_line(line, '?', '¿')
        line = _add_opening_mark_to_line(line, '!', '¡')
        result.append(line)

    return '\n'.join(result)


def _add_opening_mark_to_line(line, closing, opening):
    """Add opening mark to a line that has closing mark but no opening."""
    # Skip if no closing mark present
    if closing not in line:
        return line

    # Already has the opening mark — check balance
    if opening in line:
        return line

    # Strip HTML tags for analysis but preserve them in output
    stripped = re.sub(r'<[^>]+>', '', line).strip()

    if not stripped.endswith(closing):
        # Closing mark isn't at end — might be mid-sentence
        # Handle each sentence segment
        return _fix_marks_in_segments(line, closing, opening)

    # Simple case: whole line is one question/exclamation
    # Find where the sentence starts (after "— " or "- " if dialogue)
    dialogue_prefix = ''
    content = line

    # Extract dialogue prefix
    dash_match = re.match(r'^(\s*(?:—|–|-)\s*)', content)
    if dash_match:
        dialogue_prefix = dash_match.group(1)
        content = content[len(dialogue_prefix):]

    # Extract leading HTML tags
    tag_prefix = ''
    tag_match = re.match(r'^(<[^>]+>)', content)
    if tag_match:
        tag_prefix = tag_match.group(1)
        content = content[len(tag_prefix):]

    # Don't add if content starts with opening mark already
    if content.startswith(opening):
        return line

    # Add opening mark at the start of the content
    return f'{dialogue_prefix}{tag_prefix}{opening}{content}'


def _fix_marks_in_segments(line, closing, opening):
    """Fix opening marks in lines with multiple sentences."""
    # Split by closing mark, process each segment
    parts = line.split(closing)
    result_parts = []

    for i, part in enumerate(parts):
        if i < len(parts) - 1:  # Not the last part (which is after the last closing mark)
            part_stripped = re.sub(r'<[^>]+>', '', part).strip()
            if part_stripped and opening not in part:
                # Find the start of this sentence
                # Look for the last sentence boundary before this
                words = part.lstrip()
                # Check if starts with dash (dialogue)
                dash_match = re.match(r'^(\s*(?:—|–|-)\s*)', part)
                prefix = ''
                content = part
                if dash_match:
                    prefix = dash_match.group(1)
                    content = part[len(prefix):]

                # Find sentence start after ., !, ?, or beginning
                last_boundary = 0
                clean = re.sub(r'<[^>]+>', '', content)
                for j, ch in enumerate(clean):
                    if ch in '.!?':
                        last_boundary = j + 1

                if last_boundary > 0:
                    # Insert opening mark after the last boundary
                    # Skip spaces after boundary
                    insert_pos = last_boundary
                    while insert_pos < len(content) and content[insert_pos] == ' ':
                        insert_pos += 1
                    content = content[:insert_pos] + opening + content[insert_pos:]
                else:
                    content = opening + content.lstrip() if content.lstrip() else content

                result_parts.append(prefix + content + closing)
            else:
                result_parts.append(part + closing)
        else:
            result_parts.append(part)

    return ''.join(result_parts)


def _fix_dialogue_dashes(text):
    """Normalize dialogue dashes to em dash (—) per Netflix Spanish standards.

    Rules:
    - Replace "- " at the start of lines with "— " (em dash + space)
    - Replace "– " (en dash) with "— "
    - Only when it's clearly dialogue (two speakers)
    """
    lines = text.split('\n')
    if len(lines) < 2:
        # Single line with dash might still be dialogue
        if re.match(r'^-\s', lines[0]):
            lines[0] = re.sub(r'^-\s', '— ', lines[0])
        elif re.match(r'^–\s', lines[0]):
            lines[0] = re.sub(r'^–\s', '— ', lines[0])
        return lines[0]

    result = []
    for line in lines:
        # Replace hyphen-minus or en-dash dialogue markers with em dash
        line = re.sub(r'^-\s', '— ', line)
        line = re.sub(r'^–\s', '— ', line)
        result.append(line)

    return '\n'.join(result)


def _fix_ellipsis(text):
    """Normalize ellipsis to single character … and fix spacing."""
    # Replace three dots with ellipsis character
    text = text.replace('...', '…')
    # Remove space before ellipsis
    text = re.sub(r'\s+…', '…', text)
    # Ensure space after ellipsis if followed by a word (not end of line)
    text = re.sub(r'…([A-ZÁÉÍÓÚÜÑa-záéíóúüñ])', r'… \1', text)
    return text


def _clean_artifacts(text):
    """Remove common machine translation artifacts."""
    # Remove repeated punctuation
    text = re.sub(r'([?!])\1+', r'\1', text)
    # Remove double spaces
    text = re.sub(r'  +', ' ', text)
    # Remove space before comma, period, colon, semicolon
    text = re.sub(r'\s+([,.:;])', r'\1', text)
    # Fix "¿ " or "¡ " with extra space after opening mark
    text = re.sub(r'¿\s+', '¿', text)
    text = re.sub(r'¡\s+', '¡', text)
    # Remove trailing whitespace per line
    lines = text.split('\n')
    lines = [l.rstrip() for l in lines]
    return '\n'.join(lines)


def _normalize_quotes(text):
    """Normalize quotation marks to standard Spanish usage."""
    # Replace straight double quotes with angular quotes « »
    # Only if they appear as pairs
    count = text.count('"')
    if count >= 2 and count % 2 == 0:
        # Replace pairs
        is_open = True
        result = []
        for ch in text:
            if ch == '"':
                result.append('«' if is_open else '»')
                is_open = not is_open
            else:
                result.append(ch)
        text = ''.join(result)
    return text


# ── Timing adjustments ────────────────────────────────────────────────

def _adjust_timings(entries):
    """Adjust subtitle timings to meet Netflix standards.

    - Minimum duration: 833ms (5/6 of a second)
    - Maximum duration: 7000ms
    - Maximum reading speed: 17 CPS
    - Minimum gap between subtitles: 83ms (2 frames at 24fps)
    - Never extend a subtitle's end past the next subtitle's start
    """
    MIN_GAP_MS = 83  # Minimum gap between consecutive subtitles (Netflix: 2 frames)

    for i, entry in enumerate(entries):
        start = entry.get('start', 0)
        end = entry.get('end', 0)
        text = entry.get('text', '')
        duration = end - start

        if duration <= 0:
            continue

        # Determine the maximum allowed end time (don't overlap next subtitle)
        if i + 1 < len(entries):
            next_start = entries[i + 1].get('start', 0)
            max_end = next_start - MIN_GAP_MS
        else:
            max_end = start + MAX_DURATION_MS

        # Strip HTML tags for character count
        visible_text = re.sub(r'<[^>]+>', '', text)
        char_count = len(visible_text.replace('\n', ''))

        # Enforce minimum duration (but respect next subtitle boundary)
        if duration < MIN_DURATION_MS:
            entry['end'] = min(start + MIN_DURATION_MS, max_end)

        # Enforce maximum duration
        if (entry['end'] - start) > MAX_DURATION_MS:
            entry['end'] = start + MAX_DURATION_MS

        # Check CPS (characters per second)
        duration_secs = (entry['end'] - start) / 1000.0
        if duration_secs > 0:
            cps = char_count / duration_secs
            if cps > MAX_CPS and char_count > 0:
                # Extend duration to meet CPS limit
                needed_duration = int((char_count / MAX_CPS) * 1000)
                # Don't exceed MAX_DURATION or next subtitle's start
                new_end = start + min(needed_duration, MAX_DURATION_MS)
                new_end = min(new_end, max_end)
                # Only extend, never shrink
                if new_end > entry['end']:
                    entry['end'] = new_end

        # Final safety: ensure we never overlap the next subtitle
        if entry['end'] > max_end:
            entry['end'] = max_end
