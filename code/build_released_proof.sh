#!/bin/bash
# Independent compile of the released Lean proof. No secrets. Nothing is uploaded; only progress is printed.
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq > /dev/null 2>&1; apt-get install -y -qq curl git ca-certificates zstd > /dev/null 2>&1
curl -sSf https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | sh -s -- -y --default-toolchain none > /dev/null 2>&1
export PATH="$HOME/.elan/bin:$PATH"
mkdir -p /w && cd /w; nproc; free -g | head -2; df -h /w | tail -1
for i in $(seq -w 1 14); do curl -sfL -o part$i https://alpo.ge/lean.tar.gz.part$i || echo "DL_FAIL $i"; done
cat part* > lean.tar.gz; rm -f part*; sha256sum lean.tar.gz; tar xzf lean.tar.gz; rm -f lean.tar.gz; cd lean
echo "--- lakefile"; cat lakefile.toml; echo "--- manifest"; head -60 lake-manifest.json; echo "--- Main"; cat src/Main.lean | head -40
echo "--- RH def used"; grep -rIn --include='*.lean' -E '^(def|abbrev|structure) +RiemannHypothesis' . | head; grep -rIn -E 'import Mathlib' src/Main.lean | head -3
lake exe cache get > /tmp/cache.log 2>&1; tail -2 /tmp/cache.log
echo "BUILD_START $(date -u +%H:%M:%S)"
( while true; do sleep 300; echo "PROGRESS $(date -u +%H:%M:%S) of=175187 load=$(cut -d" " -f1 /proc/loadavg) olean=$(find .lake/build -name '*.olean' 2>/dev/null | wc -l) disk=$(du -sh .lake 2>/dev/null | cut -f1) $(tail -1 /tmp/build.log | cut -c1-160)"; done ) &
lake build > /tmp/build.log 2>&1; RC=$?
echo "BUILD_END rc=$RC $(date -u +%H:%M:%S) olean=$(find .lake/build -name '*.olean' | wc -l)"
grep -E 'error' /tmp/build.log | head -40; tail -15 /tmp/build.log
if [ $RC -eq 0 ]; then
  printf 'import Main\n#print axioms riemannHypothesis\n#check @riemannHypothesis\n' > /tmp/ax.lean
  echo "--- AXIOMS"; lake env lean /tmp/ax.lean 2>&1 | head -30
fi
echo ALL_DONE
