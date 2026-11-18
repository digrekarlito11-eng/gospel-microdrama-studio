const { describe, it } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const { AMINA_EPISODES } = require('../../js/data/episodes-data.js');

describe('AMINA Episodes Data Registry (Unit Tests)', () => {
  describe('Tier 1: Global Registry Schema & Episode Counts', () => {
    it('should contain exactly 11 episodes', () => {
      assert.ok(Array.isArray(AMINA_EPISODES), 'AMINA_EPISODES must be an array');
      assert.equal(AMINA_EPISODES.length, 11, 'Registry must contain exactly 11 episodes');
    });

    it('should have strictly sequential IDs and numbers from 1 to 11', () => {
      AMINA_EPISODES.forEach((ep, idx) => {
        const expectedNum = idx + 1;
        const expectedId = `ep-${String(expectedNum).padStart(3, '0')}`;
        assert.equal(ep.number, expectedNum, `Episode at index ${idx} must have number ${expectedNum}`);
        assert.equal(ep.id, expectedId, `Episode ${expectedNum} must have id ${expectedId}`);
      });
    });

    it('should have non-empty titles, hooks, and cliffhangers for every episode', () => {
      AMINA_EPISODES.forEach((ep) => {
        assert.ok(typeof ep.title === 'string' && ep.title.trim().length > 5, `Episode ${ep.id} missing title`);
        assert.ok(typeof ep.hook === 'string' && ep.hook.trim().length > 5, `Episode ${ep.id} missing dramatic hook`);
        assert.ok(typeof ep.cliffhanger === 'string' && ep.cliffhanger.trim().length > 5, `Episode ${ep.id} missing cliffhanger`);
      });
    });
  });

  describe('Tier 2: Freemium Rules & Tier Partitioning', () => {
    it('should partition episodes into 3 free lead magnet and 8 locked monetization episodes', () => {
      const freeEpisodes = AMINA_EPISODES.filter(e => e.isFree);
      const lockedEpisodes = AMINA_EPISODES.filter(e => !e.isFree);

      assert.equal(freeEpisodes.length, 3, 'There must be exactly 3 free episodes (ep-001, ep-002, ep-003)');
      assert.equal(lockedEpisodes.length, 8, 'There must be exactly 8 locked episodes (ep-004 to ep-011)');

      assert.deepEqual(freeEpisodes.map(e => e.id), ['ep-001', 'ep-002', 'ep-003']);
      assert.deepEqual(lockedEpisodes.map(e => e.id), [
        'ep-004', 'ep-005', 'ep-006', 'ep-007',
        'ep-008', 'ep-009', 'ep-010', 'ep-011'
      ]);
    });

    it('should mark free episodes with tier "free" and locked with tier "locked"', () => {
      AMINA_EPISODES.slice(0, 3).forEach(ep => {
        assert.equal(ep.tier, 'free');
        assert.equal(ep.isFree, true);
      });
      AMINA_EPISODES.slice(3).forEach(ep => {
        assert.equal(ep.tier, 'locked');
        assert.equal(ep.isFree, false);
      });
    });
  });

  describe('Tier 3: Subtitles & Timing Integrity', () => {
    it('should have at least 3 synchronized subtitle cues for each episode', () => {
      AMINA_EPISODES.forEach(ep => {
        assert.ok(Array.isArray(ep.subtitles), `Episode ${ep.id} subtitles must be an array`);
        assert.ok(ep.subtitles.length >= 3, `Episode ${ep.id} must have at least 3 subtitle cues`);
      });
    });

    it('should have valid cue structures with chronological timestamps', () => {
      const srtTimeRegex = /^\d{2}:\d{2}:\d{2},\d{3}$/;

      AMINA_EPISODES.forEach(ep => {
        let lastEndSeconds = -1;

        ep.subtitles.forEach((cue, cueIdx) => {
          assert.ok(cue.id, `Episode ${ep.id} cue ${cueIdx} missing id`);
          assert.match(cue.start, srtTimeRegex, `Episode ${ep.id} cue ${cueIdx} invalid start timecode: ${cue.start}`);
          assert.match(cue.end, srtTimeRegex, `Episode ${ep.id} cue ${cueIdx} invalid end timecode: ${cue.end}`);
          assert.ok(cue.startSeconds >= 0, `startSeconds must be >= 0 in ${ep.id}`);
          assert.ok(cue.endSeconds > cue.startSeconds, `endSeconds must be > startSeconds in ${ep.id} cue ${cueIdx}`);
          assert.ok(cue.startSeconds >= lastEndSeconds, `Cues should be sequential in ${ep.id} cue ${cueIdx}`);
          assert.ok(typeof cue.text === 'string' && cue.text.trim().length > 0, `cue text empty in ${ep.id}`);
          lastEndSeconds = cue.endSeconds;
        });
      });
    });
  });

  describe('Tier 4: Production Media Assets & Bible References', () => {
    it('should link to real rendered master videos for free episodes', () => {
      const baseDir = path.resolve(__dirname, '../../');

      // Ep-001
      const ep1 = AMINA_EPISODES.find(e => e.id === 'ep-001');
      assert.ok(ep1.hasLocalVideo);
      const ep1Path = path.join(baseDir, ep1.videoSrc);
      assert.ok(fs.existsSync(ep1Path), `Master video for ep-001 must exist at ${ep1Path}`);

      // Ep-002
      const ep2 = AMINA_EPISODES.find(e => e.id === 'ep-002');
      assert.ok(ep2.hasLocalVideo);
      const ep2Path = path.join(baseDir, ep2.videoSrc);
      assert.ok(fs.existsSync(ep2Path), `Master video for ep-002 must exist at ${ep2Path}`);

      // Ep-003
      const ep3 = AMINA_EPISODES.find(e => e.id === 'ep-003');
      assert.ok(ep3.hasLocalVideo);
      const ep3Path = path.join(baseDir, ep3.videoSrc);
      assert.ok(fs.existsSync(ep3Path), `Master video for ep-003 must exist at ${ep3Path}`);
    });

    it('should link to real contact sheet images for ep-001 to ep-003', () => {
      const baseDir = path.resolve(__dirname, '../../');
      ['ep-001', 'ep-002', 'ep-003'].forEach(id => {
        const ep = AMINA_EPISODES.find(e => e.id === id);
        assert.ok(ep.hasContactSheet);
        const csPath = path.join(baseDir, ep.contactSheet);
        assert.ok(fs.existsSync(csPath), `Contact sheet for ${id} must exist at ${csPath}`);
      });
    });

    it('should specify Suno prompt styles, Flow video prompts, and Psalm 91 verses for all episodes', () => {
      AMINA_EPISODES.forEach(ep => {
        assert.ok(typeof ep.sunoStyle === 'string' && ep.sunoStyle.length > 10, `ep ${ep.id} missing sunoStyle`);
        assert.ok(typeof ep.flowPrompt === 'string' && ep.flowPrompt.length > 10, `ep ${ep.id} missing flowPrompt`);
        assert.ok(ep.psalmVerse && ep.psalmVerse.ref && ep.psalmVerse.text, `ep ${ep.id} missing psalmVerse`);
        assert.ok(ep.psalmVerse.ref.startsWith('Psaume 91'), `ep ${ep.id} psalm ref should start with Psaume 91`);
        assert.equal(ep.chapterNumber, ep.number, `Episode ${ep.id} chapterNumber should match episode number`);
      });
    });
  });
});
