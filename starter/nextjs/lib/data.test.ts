import { test } from "node:test";
import assert from "node:assert/strict";
import { parseCsv } from "./data.ts";

test("parseCsv: 헤더와 따옴표 안 쉼표", () => {
  const rows = parseCsv('a,b\n1,"x,y"\n2,z\n');
  assert.equal(rows.length, 2);
  assert.deepEqual(rows[0], { a: "1", b: "x,y" });
});
