const { describe, it } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const { AMINA_BOOK } = require('../../js/data/book-data.js');

describe('AMINA Book Data Registry (Unit Tests)', () => {
  const baseDir = path.resolve(__dirname, '../../');

  describe('Tier 1: Book Meta & Canonical Authorship', () => {
    it('should have correct book metadata and inspiration', () => {
      assert.ok(AMINA_BOOK.meta, 'AMINA_BOOK must have a meta object');
      assert.equal(AMINA_BOOK.meta.title, "AMINA : L'Autel De Yopougon — La Guerre Invisible");
      assert.equal(AMINA_BOOK.meta.author, 'Karl DIGRÉ');
      assert.ok(AMINA_BOOK.meta.spiritualInspiration.includes('Yvan Castanou'), 'Must acknowledge Pastor Yvan Castanou');
      assert.ok(AMINA_BOOK.meta.spiritualInspiration.includes('hupopiazo'), 'Must mention hupopiazo / persistent prayer');
      assert.equal(AMINA_BOOK.meta.commercialContact, '+225 07 00 88 95 14');
      assert.equal(AMINA_BOOK.meta.whatsappUrl, 'https://wa.me/2250700889514');
      assert.equal(AMINA_BOOK.meta.totalChapters, 11);
    });

    it('should reference existing official cover image', () => {
      const coverPath = path.join(baseDir, AMINA_BOOK.meta.coverImage);
      assert.ok(fs.existsSync(coverPath), `Cover image must exist at ${coverPath}`);
      const stats = fs.statSync(coverPath);
      assert.ok(stats.size > 50000, 'Cover image file size must be substantial (> 50 KB)');
    });
  });

  describe('Tier 2: Front Matter (Préambule) Integrity', () => {
    it('should contain Dédicace with faithful content', () => {
      const { dedicace } = AMINA_BOOK.preambule;
      assert.ok(dedicace, 'Must have dedicace section');
      assert.equal(dedicace.title, 'Dédicace');
      assert.ok(dedicace.content.includes('Dieu le Père'), 'Dédicace must dedicate to God the Father');
      assert.ok(dedicace.content.includes('veuve importune'), 'Must reference importunate widow');
      assert.ok(dedicace.content.includes('Karl DIGRÉ'), 'Must be signed Karl DIGRÉ');
      assert.ok(Array.isArray(dedicace.paragraphs) && dedicace.paragraphs.length > 0);
    });

    it('should contain Préface explaining the genesis in Abidjan', () => {
      const { preface } = AMINA_BOOK.preambule;
      assert.ok(preface, 'Must have preface section');
      assert.equal(preface.title, 'Préface');
      assert.ok(preface.content.includes('Abidjan'), 'Préface must reference Abidjan');
      assert.ok(preface.content.includes('La prière qui n\'échoue jamais'), 'Must cite Castanou work');
      assert.ok(Array.isArray(preface.paragraphs) && preface.paragraphs.length >= 3);
    });

    it('should contain Introduction explaining persistent prayer (hupopiazo)', () => {
      const { introduction } = AMINA_BOOK.preambule;
      assert.ok(introduction, 'Must have introduction section');
      assert.ok(introduction.title.includes('Persévérance'));
      assert.ok(introduction.content.includes('hupopiazo'), 'Must explain hupopiazo');
      assert.ok(introduction.content.includes('Yopougon'), 'Must reference Yopougon');
      assert.ok(Array.isArray(introduction.paragraphs) && introduction.paragraphs.length >= 3);
    });
  });

  describe('Tier 3: Chapters Corpus & Structure', () => {
    it('should contain exactly 11 chapters sequentially ordered', () => {
      assert.ok(Array.isArray(AMINA_BOOK.chapters));
      assert.equal(AMINA_BOOK.chapters.length, 11);

      AMINA_BOOK.chapters.forEach((chap, idx) => {
        const expectedNum = idx + 1;
        const expectedId = `chapitre-${String(expectedNum).padStart(2, '0')}`;
        assert.equal(chap.number, expectedNum, `Chapter at index ${idx} number mismatch`);
        assert.equal(chap.id, expectedId, `Chapter at index ${idx} id mismatch`);
        assert.equal(chap.episodeId, `ep-${String(expectedNum).padStart(3, '0')}`, 'Transmedia link to episode ID must match');
      });
    });

    it('should verify each chapter has substantial text, word count and reading time', () => {
      AMINA_BOOK.chapters.forEach((chap) => {
        assert.ok(typeof chap.title === 'string' && chap.title.length > 5, `${chap.id} title invalid`);
        const text = chap.rawContent || (chap.paragraphs && chap.paragraphs.join('\n'));
        assert.ok(typeof text === 'string' && text.length > 1000, `${chap.id} text too short (< 1000 chars)`);
        assert.ok(chap.wordCount > 300, `${chap.id} word count must be > 300 (got ${chap.wordCount})`);
        assert.ok(chap.readingTimeMinutes > 0, `${chap.id} readingTimeMinutes must be > 0`);
        assert.ok(Array.isArray(chap.paragraphs) && chap.paragraphs.length >= 5, `${chap.id} paragraphs must have at least 5 paragraphs`);
      });
    });

    it('should assign a unique Psalm 91 verse to each chapter', () => {
      const verses = new Set();
      AMINA_BOOK.chapters.forEach((chap) => {
        assert.ok(chap.psalmVerse && chap.psalmVerse.ref && chap.psalmVerse.text, `${chap.id} missing psalm verse`);
        assert.ok(chap.psalmVerse.ref.startsWith('Psaume 91:'), `${chap.id} verse must be from Psalm 91`);
        verses.add(chap.psalmVerse.ref);
      });
      assert.ok(verses.size >= 10, 'Each chapter should have a distinctive Psalm 91 verse');
    });

    it('should cross-verify chapter text matching source markdown files on disk', () => {
      for (let i = 1; i <= 11; i++) {
        const fileNum = String(i).padStart(2, '0');
        const srcFile = path.join(baseDir, `source/chapitre-${fileNum}.md`);
        assert.ok(fs.existsSync(srcFile), `Source file ${srcFile} must exist`);

        const diskContent = fs.readFileSync(srcFile, 'utf8');
        const registryChap = AMINA_BOOK.chapters.find(c => c.number === i);
        assert.ok(registryChap, `Registry missing chapter ${i}`);

        // Check first heading from disk matches chapter title or content
        const firstLine = diskContent.split('\n').filter(l => l.trim().length > 0)[0];
        const cleanTitle = firstLine.replace(/^#+\s*/, '').trim();
        assert.ok(
          registryChap.title.includes(cleanTitle) ||
          registryChap.rawContent.includes(cleanTitle),
          `Chapter ${i} should reflect title from source file`
        );
      }
    });
  });

  describe('Tier 4: End Matter & Practical Guide (Conclusion)', () => {
    it('should include the complete practical prayer guide', () => {
      const guide = AMINA_BOOK.guide;
      assert.ok(guide, 'Must include guide object');
      assert.ok(guide.title.includes('Guide Pratique'));
      assert.ok(guide.rawContent && guide.rawContent.length > 50);
      assert.ok(Array.isArray(guide.principles));
      assert.equal(guide.principles.length, 3, 'Must have 3 core spiritual principles');
    });

    it('should define the 3 spiritual principles faithful to Castanou teaching', () => {
      const [p1, p2, p3] = AMINA_BOOK.guide.principles;

      assert.equal(p1.number, 1);
      assert.ok(p1.title.includes('diable respirer'), 'Principle 1 title');
      assert.ok(p1.summary.length > 20);

      assert.equal(p2.number, 2);
      assert.ok(p2.title.includes('Esprit') || p2.title.includes('Hupopiazo'), 'Principle 2 title');

      assert.equal(p3.number, 3);
      assert.ok(p3.title.includes('capitulation'), 'Principle 3 title');
    });

    it('should provide the commercial contact notice', () => {
      const notice = AMINA_BOOK.guide.commercialNotice;
      assert.ok(notice.includes('+225 07 00 88 95 14'), 'Must include official WhatsApp number');
    });
  });
});
