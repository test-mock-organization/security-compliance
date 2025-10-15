# Security Notice: vulnerability in common npm Packages

## Summary

We’ve been informed about a vulnerability affecting several npm packages. These packages may be present in some of our repositories!

## What we're doing

- We are scanning all repositories in our organization on GitHub to identify any usage of the affected packages.
- Once impacted repositories are identified, we will reach out directly through Github Issues on those repositories.

## What you need to do

- Do not update or change dependencies unless you receive specific guidance.
- If you maintain a repository with a `package.json` file, please keep an eye out for direct communication from the Platform team in the Issues section of your repo.
- Stay informed by checking impacted packages on https://www.aikido.dev/blog/s1ngularity-nx-attackers-strike-again or the `vulnerable_packages.json` (can be found in this repo in `/data`) and any updates we provide through official channels.

## Stay secure :)

This is a great reminder to:
- Regularly checck your dependencies
- Use `npm audit` to spot vulnerabilities
- Review PRs for dependency changes carefully

Thank you for your attention and support in keeping our codebase secure.  
If you have any immediate concerns, reach out to the Platform Engineering team.

## Resources

If you want to know more, here are a few links:
- https://www.aikido.dev/blog/s1ngularity-nx-attackers-strike-again
- https://www.youtube.com/watch?v=vuPLmzKUIlc
- https://www.wiz.io/blog/shai-hulud-npm-supply-chain-attack