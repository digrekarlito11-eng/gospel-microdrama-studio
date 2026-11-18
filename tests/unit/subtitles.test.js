const { describe, it } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const { AMINA_EPISODES } = require('../../js/data/episodes-data.js');

/**
 * Standard SRT Parser & Timecode Utilities
 * Follows SubRip (.srt) specification (RFC/Matroska SRT spec)
 */
function timecodeToSeconds(timecode) {
  if (!timecode || typeof timecode !== 'string') return 0;
  // Match HH:MM:SS,mmm or HH:MM:SS.mmm
  const match = timecode.trim().match(/^(\d{2}):(\d{2}):(\d{2})[,.](\d{3})$/);
  if (!match) return 0;
  const hours = parseInt(match[1], 10);
  const minutes = parseInt(match[2], 10);
  const seconds = parseInt(match[3], 10);
  const millis = parseInt(match[4], 10);
  return hours * 3600 + minutes * 60 + seconds + millis / 1000;
}

function secondsToTimecode(totalSeconds) {
  if (typeof totalSeconds !== 'number' || isNaN(totalSeconds) || totalSeconds < 0) {
    return '00:00:00,000';
  }
  const hours = Math.floor(totalSeconds / 3600);
  const remainder = totalSeconds % 3600;
  const minutes = Math.floor(remainder / 60);
  const seconds = Math.floor(remainder % 60);
  const millis = Math.round((totalSeconds - Math.floor(totalSeconds)) * 1000);

  const pad = (n, w = 2) => String(n).padStart(w, '0');
  return `${pad(hours)}:${pad(minutes)}:${pad(seconds)},${pad(millis, 3)}`;
}

function parseSrt(srtContent) {
  if (!srtContent || typeof srtContent !== 'string') return [];

  // Normalize line endings to LF
  const normalized = srtContent.replace(/\r\n/g, '\n').replace(/\r/g, '\n').trim();
  if (!normalized) return [];

  // Split on double newlines separating blocks
  const blocks = normalized.split(/\n\s*\n/);
  const cues = [];

  for (const block of blocks) {
    const lines = block.split('\n').map(l => l.trimEnd()).filter(l => l.length > 0);
    if (lines.length < 2) continue;

    let id = '';
    let timeLine = '';
    let textLines = [];

    // Check if line 0 is numeric ID
    if (/^\d+$/.test(lines[0])) {
      id = lines[0];
      timeLine = lines[1] || '';
      textLines = lines.slice(2);
    } else if (lines[0].includes('-->')) {
      timeLine = lines[0];
      textLines = lines.slice(1);
    } else {
      continue;
    }

    const timeParts = timeLine.split('-->').map(p => p.trim());
    if (timeParts.length !== 2) continue;

    const start = timeParts[0];
    const end = timeParts[1];
    const startSeconds = timecodeToSeconds(start);
    const endSeconds = timecodeToSeconds(end);
    const text = textLines.join('\n').trim();

    if (text) {
      cues.push({
        id: id || String(cues.length + 1),
        start,
        end,
        startSeconds,
        endSeconds,
        text
      });
    }
  }

  return cues;
}

describe('Subtitles Parser & Timecode Utilities (Unit Tests)', () => {
  const baseDir = path.resolve(__dirname, '../../');

  describe('Tier 1: Timecode Conversion', () => {
    it('should accurately convert standard SRT timecodes to decimal seconds', () => {
      assert.equal(timecodeToSeconds('00:00:00,500'), 0.5);
      assert.equal(timecodeToSeconds('00:00:04,500'), 4.5);
      assert.equal(timecodeToSeconds('00:00:15,000'), 15.0);
      assert.equal(timecodeToSeconds('00:01:05,000'), 65.0);
      assert.equal(timecodeToSeconds('00:01:14,500'), 74.5);
      assert.equal(timecodeToSeconds('01:00:00,000'), 3600.0);
      assert.equal(timecodeToSeconds('01:23:45,678'), 5025.678);
    });

    it('should support dot separator as WebVTT fallback', () => {
      assert.equal(timecodeToSeconds('00:01:10.250'), 70.25);
    });

    it('should convert decimal seconds back to standard SRT timecode', () => {
      assert.equal(secondsToTimecode(0.5), '00:00:00,500');
      assert.equal(secondsToTimecode(65.0), '00:01:05,000');
      assert.equal(secondsToTimecode(74.5), '00:01:14,500');
      assert.equal(secondsToTimecode(5025.678), '01:23:45,678');
    });

    it('should safely handle invalid or out-of-bounds timecodes', () => {
      assert.equal(timecodeToSeconds(null), 0);
      assert.equal(timecodeToSeconds(''), 0);
      assert.equal(timecodeToSeconds('invalid:timecode'), 0);
      assert.equal(secondsToTimecode(-10), '00:00:00,000');
      assert.equal(secondsToTimecode(NaN), '00:00:00,000');
    });
  });

  describe('Tier 2: SRT Parsing & Multiline Handling', () => {
    it('should parse single cue SRT with sequence, timestamps, and text', () => {
      const srt = `1\n00:00:00,500 --> 00:00:04,500\nÀ Yopougon, quand la nuit tombe...`;
      const cues = parseSrt(srt);
      assert.equal(cues.length, 1);
      assert.equal(cues[0].id, '1');
      assert.equal(cues[0].start, '00:00:00,500');
      assert.equal(cues[0].end, '00:00:04,500');
      assert.equal(cues[0].startSeconds, 0.5);
      assert.equal(cues[0].endSeconds, 4.5);
      assert.equal(cues[0].text, 'À Yopougon, quand la nuit tombe...');
    });

    it('should handle multiline dialogue text within a single cue', () => {
      const multilineSrt = `1\n00:00:05,000 --> 00:00:10,000\nZagba: Tout s'achète à Yopougon.\nAmina: Pas ma foi.\n\n2\n00:00:11,000 --> 00:00:15,000\nKoffi: Nous verrons bien.`;
      const cues = parseSrt(multilineSrt);
      assert.equal(cues.length, 2);
      assert.equal(cues[0].text, "Zagba: Tout s'achète à Yopougon.\nAmina: Pas ma foi.");
      assert.equal(cues[1].text, 'Koffi: Nous verrons bien.');
    });

    it('should correctly handle Windows CRLF line endings', () => {
      const crlfSrt = "1\r\n00:00:01,000 --> 00:00:03,000\r\nLigne 1\r\n\r\n2\r\n00:00:04,000 --> 00:00:06,000\r\nLigne 2\r\n";
      const cues = parseSrt(crlfSrt);
      assert.equal(cues.length, 2);
      assert.equal(cues[0].text, 'Ligne 1');
      assert.equal(cues[1].text, 'Ligne 2');
    });

    it('should gracefully handle empty or malformed inputs', () => {
      assert.deepEqual(parseSrt(''), []);
      assert.deepEqual(parseSrt('   \n\n  '), []);
      assert.deepEqual(parseSrt(null), []);
      assert.deepEqual(parseSrt('random unformatted text without timestamps'), []);
    });
  });

  describe('Tier 3: Repository Integration & Subtitle Integrity Verification', () => {
    it('should parse every episode subtitles.srt file on disk and verify alignment with data registry', () => {
      for (let i = 1; i <= 11; i++) {
        const epNumStr = String(i).padStart(3, '0');
        const srtPath = path.join(baseDir, `episodes/ep-${epNumStr}/subtitles.srt`);
        assert.ok(fs.existsSync(srtPath), `SRT file must exist at ${srtPath}`);

        const srtContent = fs.readFileSync(srtPath, 'utf8');
        const parsedCues = parseSrt(srtContent);

        assert.ok(parsedCues.length >= 3, `ep-${epNumStr} must parse into at least 3 cues`);

        // Cross-verify with AMINA_EPISODES precompiled registry
        const registryEp = AMINA_EPISODES.find(e => e.id === `ep-${epNumStr}`);
        assert.ok(registryEp, `Missing ep-${epNumStr} in registry`);
        assert.equal(
          parsedCues.length,
          registryEp.subtitles.length,
          `Cue count mismatch for ep-${epNumStr}`
        );

        parsedCues.forEach((cue, cueIdx) => {
          const regCue = registryEp.subtitles[cueIdx];
          assert.equal(cue.start, regCue.start, `Cue ${cueIdx} start mismatch in ep-${epNumStr}`);
          assert.equal(cue.end, regCue.end, `Cue ${cueIdx} end mismatch in ep-${epNumStr}`);
          assert.equal(cue.text.trim(), regCue.text.trim(), `Cue ${cueIdx} text mismatch in ep-${epNumStr}`);
        });
      }
    });
  });
});
