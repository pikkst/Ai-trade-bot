#!/usr/bin/env node
// eslint-env node
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const exceptionsFile = path.join(__dirname, 'npm-audit-exceptions.md');
const exceptions = fs.readFileSync(exceptionsFile, 'utf8');

let auditData;
try {
  const output = execSync('npm audit --json', {
    cwd: __dirname,
    encoding: 'utf8',
    stdio: ['pipe', 'pipe', 'pipe'],
  });
  auditData = JSON.parse(output);
} catch (e) {
  const stderr = e.stderr || '';
  try {
    auditData = JSON.parse(stderr);
  } catch {
    console.error('Failed to parse npm audit output');
    process.exit(1);
  }
}

const vulns = auditData.vulnerabilities || {};
const allowlisted = new Set();

const ghsaMatches = exceptions.match(/GHSA-[a-zA-Z0-9]+/g) || [];
ghsaMatches.forEach((id) => allowlisted.add(id));

const packageMatches = exceptions.match(/\*\*Package\*\*:\s*\S+/g) || [];
packageMatches.forEach((m) => {
  const pkg = m.replace(/\*\*Package\*\*:\s*/, '');
  allowlisted.add(pkg);
});

const nonAllowlisted = [];
for (const [name, info] of Object.entries(vulns)) {
  const advisories = info.via || [];
  const hasAllowlistedAdvisory = advisories.some((a) => {
    if (typeof a === 'string' && a.startsWith('GHSA-')) return allowlisted.has(a);
    if (typeof a === 'object' && a.url && a.url.includes('GHSA-')) {
      const ghsaId = a.url.match(/GHSA-[a-zA-Z0-9]+/);
      return ghsaId && allowlisted.has(ghsaId[0]);
    }
    return false;
  });
  const isAllowlistedPackage = allowlisted.has(name);
  if (!hasAllowlistedAdvisory && !isAllowlistedPackage) {
    nonAllowlisted.push({ name, severity: info.severity, via: advisories });
  }
}

if (nonAllowlisted.length > 0) {
  console.error('Non-allowlisted vulnerabilities found:');
  nonAllowlisted.forEach((v) => {
    console.error(`  ${v.name} (${v.severity}): ${JSON.stringify(v.via)}`);
  });
  process.exit(1);
}

console.log('All vulnerabilities are documented in npm-audit-exceptions.md');
