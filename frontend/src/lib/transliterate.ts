const DIRECT_MAP: Record<string, string> = {
  a: "अ",
  b: "ब",
  c: "क",
  d: "द",
  e: "ए",
  f: "फ",
  g: "ग",
  h: "ह",
  i: "इ",
  j: "ज",
  k: "क",
  l: "ल",
  m: "म",
  n: "न",
  o: "ओ",
  p: "प",
  q: "क",
  r: "र",
  s: "स",
  t: "ट",
  u: "उ",
  v: "व",
  w: "व",
  x: "क्स",
  y: "य",
  z: "ज़",
};

const CLUSTER_MAP: Array<[string, string]> = [
  ["tion", "शन"],
  ["sion", "ज़न"],
  ["ing", "िंग"],
  ["sh", "श"],
  ["ch", "च"],
  ["th", "थ"],
  ["ph", "फ"],
  ["kh", "ख"],
  ["gh", "घ"],
  ["aa", "आ"],
  ["ee", "ई"],
  ["oo", "ऊ"],
  ["ai", "ऐ"],
  ["au", "औ"],
  ["ou", "औ"],
];

const transliterateWord = (word: string) => {
  const lower = word.toLowerCase();
  let cursor = 0;
  let out = "";

  while (cursor < lower.length) {
    const cluster = CLUSTER_MAP.find(([latin]) => lower.startsWith(latin, cursor));
    if (cluster) {
      out += cluster[1];
      cursor += cluster[0].length;
      continue;
    }

    const char = lower[cursor];
    out += DIRECT_MAP[char] ?? word[cursor];
    cursor += 1;
  }

  return out;
};

export const transliterateToHindi = (input: string) =>
  input.replace(/[A-Za-z][A-Za-z0-9@._/-]*/g, (segment) => {
    if (/^(https?:|www\.|[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,})$/i.test(segment)) {
      return segment;
    }
    return transliterateWord(segment);
  });
