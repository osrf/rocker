# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

<!-- insertion marker -->
## [v0.2.15](https://github.com/osrf/rocker/releases/tag/v0.2.15) - 2024-03-01

<small>[Compare with v0.2.14](https://github.com/osrf/rocker/compare/v0.2.14...v0.2.15)</small>

### Added

- Add changelog ([39a2842](https://github.com/osrf/rocker/commit/39a2842d03fec73b4b0d70c3922c4ab1c93c2cc0) by Tully Foote).
- Add a shorthand option for switching to alternate rmws (#268) ([35e68c1](https://github.com/osrf/rocker/commit/35e68c17232a50cfb3a781b066e2c0d6691cb07e) by Tully Foote).

## [v0.2.14](https://github.com/osrf/rocker/releases/tag/v0.2.14) - 2024-01-26

<small>[Compare with v0.2.13](https://github.com/osrf/rocker/compare/v0.2.13...v0.2.14)</small>

### Removed

- Remove deprecated use of pkg_resources (#265) ([998761f](https://github.com/osrf/rocker/commit/998761f919302f29db2377f53efb5cb472c335fa) by Tully Foote).

## [v0.2.13](https://github.com/osrf/rocker/releases/tag/v0.2.13) - 2023-12-10

<small>[Compare with v0.2.12](https://github.com/osrf/rocker/compare/v0.2.12...v0.2.13)</small>

### Added

- Add indirection for changes in empy 3 vs 4 (#261) ([4de56c1](https://github.com/osrf/rocker/commit/4de56c18cdac09f3a9ec62a6b81cca7a4cdd46aa) by Tully Foote).
- add simple test of CLI (#256) ([6d276a4](https://github.com/osrf/rocker/commit/6d276a4fe965f50246e2ff5eb0a03c9f16ed06c8) by Tully Foote).
- Add extension ordering (#242) ([3afa6ac](https://github.com/osrf/rocker/commit/3afa6acbf6b0323f540ac16c2a0091b29099086a) by agyoungs).

### Fixed

- fix: nvidia arg (#234) ([2b8d5ab](https://github.com/osrf/rocker/commit/2b8d5abb18c829d22f290679b739dc53765198ad) by Amadeusz Szymko).
- Fix nvidia runtime fail on arm64 & add --group-add plugin (#211) ([e01d9cc](https://github.com/osrf/rocker/commit/e01d9cca8672e0a85b7ff42118ee456c4c414d9e) by Amadeusz Szymko).

### Removed

- Remove old tutorial links (#254) ([41502b3](https://github.com/osrf/rocker/commit/41502b3f41e7d36bc108d9685bce61b6d27286bc) by Tully Foote).

## [v0.2.12](https://github.com/osrf/rocker/releases/tag/v0.2.12) - 2023-05-04

<small>[Compare with v0.2.11](https://github.com/osrf/rocker/compare/v0.2.11...v0.2.12)</small>

### Fixed

- Fix default logic for user-preserve-groups (#224) ([04cfc29](https://github.com/osrf/rocker/commit/04cfc290351a60b7df28c7eff67dc2c27e9ab918) by Tully Foote).

## [v0.2.11](https://github.com/osrf/rocker/releases/tag/v0.2.11) - 2023-05-04

<small>[Compare with v0.2.10](https://github.com/osrf/rocker/compare/v0.2.10...v0.2.11)</small>

### Added

- adding debian bookworm support ([b00c1c6](https://github.com/osrf/rocker/commit/b00c1c6e2832c6d375f8b12bcee8fe74642ef043) by Tully Foote).
- add error messages for group issues ([4ce4e29](https://github.com/osrf/rocker/commit/4ce4e29041ac81830f78e1b00afbff9168194929) by Tully Foote).
- Adding a permissive option to user-preserve-groups incase there are groups on the host that aren't permissible on the target but you'd like best-effort. ([44f7946](https://github.com/osrf/rocker/commit/44f7946653f1d58cbf52a088f8c482090f5f033c) by Tully Foote).
- add link to mp_rocker (#213) ([49a23e7](https://github.com/osrf/rocker/commit/49a23e70a3055898daba80fc35f1742dc01d9a09) by Tully Foote).
- Add ability to preserve host user groups inside container ([b16136e](https://github.com/osrf/rocker/commit/b16136e589ace3519e4b5c85697e770b29a151fa) by Miguel Prada).
- Add port and expose extensions with tests (#201) ([2770045](https://github.com/osrf/rocker/commit/27700451d0b1a0701d8fe5c80c64a52942b61ce0) by Will Baker).
- Added note for linking Intel Xe cards with rocker (#190) ([3a2bf74](https://github.com/osrf/rocker/commit/3a2bf74209f577f666857054095a57bbeb3c6c1d) by Zahi Kakish).

### Removed

- Removed '-v' for rocker's version. Only --version should be available. (#205) ([67a4142](https://github.com/osrf/rocker/commit/67a414278c5940d587b9e3060eb7ab9e2e293510) by George Stavrinos).

## [v0.2.10](https://github.com/osrf/rocker/releases/tag/v0.2.10) - 2022-07-30

<small>[Compare with v0.2.9](https://github.com/osrf/rocker/compare/v0.2.9...v0.2.10)</small>

## [v0.2.9](https://github.com/osrf/rocker/releases/tag/v0.2.9) - 2022-03-23

<small>[Compare with v0.2.8](https://github.com/osrf/rocker/compare/v0.2.8...v0.2.9)</small>

## [v0.2.8](https://github.com/osrf/rocker/releases/tag/v0.2.8) - 2022-02-14

<small>[Compare with v0.2.7](https://github.com/osrf/rocker/compare/v0.2.7...v0.2.8)</small>

## [v0.2.7](https://github.com/osrf/rocker/releases/tag/v0.2.7) - 2021-12-01

<small>[Compare with v0.2.6](https://github.com/osrf/rocker/compare/v0.2.6...v0.2.7)</small>

### Added

- add an option to preserve the home directory instead of deleting it if the uid or username collide (#164) ([0f1c7d1](https://github.com/osrf/rocker/commit/0f1c7d19da389be5d37977d2e4c8b87a4c5fe1e2) by Tully Foote).

## [v0.2.6](https://github.com/osrf/rocker/releases/tag/v0.2.6) - 2021-10-05

<small>[Compare with v0.2.5](https://github.com/osrf/rocker/compare/v0.2.5...v0.2.6)</small>

## [v0.2.5](https://github.com/osrf/rocker/releases/tag/v0.2.5) - 2021-10-05

<small>[Compare with v0.2.4](https://github.com/osrf/rocker/compare/v0.2.4...v0.2.5)</small>

### Added

- Add an option to tag the image (#159) ([ef09014](https://github.com/osrf/rocker/commit/ef0901419dd99132bef5c1b797892927e63f5925) by Tully Foote).

## [v0.2.4](https://github.com/osrf/rocker/releases/tag/v0.2.4) - 2021-08-03

<small>[Compare with 0.2.3](https://github.com/osrf/rocker/compare/0.2.3...v0.2.4)</small>

### Added

- add an action to mirror main to master Providing backwards compatibility for renaming master to main ([9d7a392](https://github.com/osrf/rocker/commit/9d7a3924cd0d9a4c45ea163a7ab5296e4cdfdd3c) by Tully Foote).
- Add the privileged extension (#132) ([4214d73](https://github.com/osrf/rocker/commit/4214d73aeb3de235153905344d14ee18edc3c229) by Gaël Écorchard).
- Add --nocleanup option (#111) ([5507dc5](https://github.com/osrf/rocker/commit/5507dc510c3e339beb3573e52dcc77d8585bb285) by Tim Redick).

### Fixed

- Fix detector for the deprecated distro syntax (#156) ([2760838](https://github.com/osrf/rocker/commit/2760838dc4bc8c3bd436344ec8ab9225ad914696) by Tully Foote).
- Fix os detection for non-root images (cont.) (#150) ([8ecaf53](https://github.com/osrf/rocker/commit/8ecaf530cc374b30be121eef7a324b8200788eea) by Miguel Prada).

### Removed

- Remove intermediate containers and name os_detect images (#133) ([80602eb](https://github.com/osrf/rocker/commit/80602eb6868a9044279d88c13650828f654a32f9) by Daniel Stonier).
- Remove redundant device additions to docker_args ([a759fe6](https://github.com/osrf/rocker/commit/a759fe6b241edf37b95d104f238eb6ef9fb3d70b) by Peter Polidoro).

## [0.2.3](https://github.com/osrf/rocker/releases/tag/0.2.3) - 2020-11-25

<small>[Compare with v0.2.2](https://github.com/osrf/rocker/compare/v0.2.2...0.2.3)</small>

### Added

- add x11 flags to examples (#104) ([ae7d3f6](https://github.com/osrf/rocker/commit/ae7d3f6edcd74cb74b345f005f401061b33bda3a) by Tully Foote).
- add the ability to inject an arbitrary file which can be used via a COPY command in the snippet (#101) ([eef5516](https://github.com/osrf/rocker/commit/eef5516e65a992832be6d30a9c12459e582cba7c) by Tully Foote).
- Added --name argument ([019a543](https://github.com/osrf/rocker/commit/019a543afb759664751afe847162ab9ba09db889) by ahcorde).

### Fixed

- Fix using rocker for non-root containers (#50) ([3585298](https://github.com/osrf/rocker/commit/35852984cc4554bbfcf55f3612fa17cc89d5d715) by Johannes Meyer).

## [v0.2.2](https://github.com/osrf/rocker/releases/tag/v0.2.2) - 2020-06-24

<small>[Compare with v0.2.1](https://github.com/osrf/rocker/compare/v0.2.1...v0.2.2)</small>

## [v0.2.1](https://github.com/osrf/rocker/releases/tag/v0.2.1) - 2020-06-24

<small>[Compare with v0.2.0](https://github.com/osrf/rocker/compare/v0.2.0...v0.2.1)</small>

### Added

- add bullseye target too ([b9f407b](https://github.com/osrf/rocker/commit/b9f407ba5423c61bd9dd0a46f36d21cd7e795adf) by Tully Foote).
- add focal as a target ([55b704f](https://github.com/osrf/rocker/commit/55b704f575dc5f6af1150e29fb18faf51cfa3336) by Tully Foote).

## [v0.2.0](https://github.com/osrf/rocker/releases/tag/v0.2.0) - 2020-05-08

<small>[Compare with v0.1.10](https://github.com/osrf/rocker/compare/v0.1.10...v0.2.0)</small>

### Added

- Add support for focal and buster (#83) ([a76acb2](https://github.com/osrf/rocker/commit/a76acb2aafb1c5d5609e923b42d8d2a351e28906) by Tully Foote).
- Add support for --env-file option pass through (#82) ([135e73f](https://github.com/osrf/rocker/commit/135e73fc11cb1a6751cda6253efa26d543345e47) by Tully Foote).
- Add an Extension Manager class (#77) ([413d25a](https://github.com/osrf/rocker/commit/413d25a7e578d4eab410eda99042cabb8dc8026b) by Tully Foote).
- add codeowners so I get auto review requested (#74) ([15b604b](https://github.com/osrf/rocker/commit/15b604be5d1a940e4e242dbebff45d9298fcb787) by Tully Foote).

### Fixed

- Fix documentation for User extension (#81) ([6e9ee9c](https://github.com/osrf/rocker/commit/6e9ee9c96aa2664b51974724377cd771c465dbbf) by Emerson Knapp).
- Fix import paths (#76) ([d26004b](https://github.com/osrf/rocker/commit/d26004b2dcc919bf08ae7aeeef0e669f0a66a7f4) by Tully Foote).

## [v0.1.10](https://github.com/osrf/rocker/releases/tag/v0.1.10) - 2019-12-05

<small>[Compare with v0.1.9](https://github.com/osrf/rocker/compare/v0.1.9...v0.1.10)</small>

## [v0.1.9](https://github.com/osrf/rocker/releases/tag/v0.1.9) - 2019-10-14

<small>[Compare with v0.1.8](https://github.com/osrf/rocker/compare/v0.1.8...v0.1.9)</small>

### Added

- Add verbosity outputs ([6246570](https://github.com/osrf/rocker/commit/6246570e1630592c9426e64c7477d53339edc568) by Tully Foote).

### Removed

- Remove xvfb-run which started failing CI. (#69) ([d38927a](https://github.com/osrf/rocker/commit/d38927ab13ffe6ccf84bb9408261feb6a3df3231) by Tully Foote).

## [v0.1.8](https://github.com/osrf/rocker/releases/tag/v0.1.8) - 2019-09-18

<small>[Compare with v0.1.7](https://github.com/osrf/rocker/compare/v0.1.7...v0.1.8)</small>

### Added

- Add a version cli option (#65) ([28fc9ff](https://github.com/osrf/rocker/commit/28fc9ff1fab435ab71c1077ac6882380d38d66f1) by Tully Foote).

### Fixed

- FIx the window resize (#66) ([7757df0](https://github.com/osrf/rocker/commit/7757df091bee54714368a2d08236f6ba9caf4bc5) by Tully Foote).

## [v0.1.7](https://github.com/osrf/rocker/releases/tag/v0.1.7) - 2019-09-17

<small>[Compare with v0.1.6](https://github.com/osrf/rocker/compare/v0.1.6...v0.1.7)</small>

### Added

- add --home (#64) ([733e29b](https://github.com/osrf/rocker/commit/733e29b7521a4037ba381d3d219cabaf3855a608) by Tully Foote).
- Add sigwinch passthrough for xterm resizing (#57) ([efec0f9](https://github.com/osrf/rocker/commit/efec0f964a12b239f6c201498b2aa478fe56d83c) by Ruffin).
- Add new extensions git and ssh (#58) ([5405f3f](https://github.com/osrf/rocker/commit/5405f3fc824b3948772c6b60efff4370954497d3) by Johannes Meyer).

### Fixed

- Fix sudo with user extension for some usernames (#55) ([0bc20b8](https://github.com/osrf/rocker/commit/0bc20b84c72d16b5f81dda59283c6e242e203938) by Johannes Meyer).

## [v0.1.6](https://github.com/osrf/rocker/releases/tag/v0.1.6) - 2019-08-29

<small>[Compare with 0.1.5](https://github.com/osrf/rocker/compare/0.1.5...v0.1.6)</small>

## [0.1.5](https://github.com/osrf/rocker/releases/tag/0.1.5) - 2019-08-28

<small>[Compare with 0.1.4](https://github.com/osrf/rocker/compare/0.1.4...0.1.5)</small>

### Added

- Add extension to pass custom environment variables (#51) ([e27cc0b](https://github.com/osrf/rocker/commit/e27cc0bb8d6677807a9c791470b023253569fedf) by Johannes Meyer).
- Add Cosmic, Disco, and Eoan suites. ([daf23a7](https://github.com/osrf/rocker/commit/daf23a7ca4f10e557e1dcdf9edb854b83d2186bf) by Steven! Ragnarök).

### Fixed

- Fix OS detection (fix #43) ([7a419f9](https://github.com/osrf/rocker/commit/7a419f91b0e8aa0fb0beae040844b4ed77e3f7a1) by Johannes Meyer).

### Removed

- remove unused imports ([39118bb](https://github.com/osrf/rocker/commit/39118bb877553364f70e082be24aaf07559f7ef4) by Tully Foote).

## [0.1.4](https://github.com/osrf/rocker/releases/tag/0.1.4) - 2019-03-13

<small>[Compare with 0.1.3](https://github.com/osrf/rocker/compare/0.1.3...0.1.4)</small>

### Added

- add documentation about how to use an intel integrated graphics card ([f03299f](https://github.com/osrf/rocker/commit/f03299ffddeb3d050f1f16cb048e2a9983895d90) by Tully Foote).
- Add No-Python2 flag ([101813f](https://github.com/osrf/rocker/commit/101813fa2fdf75d80e628ee0871d8cb238e11337) by Tully Foote).
- adding coverage of nvidia ([6f8121f](https://github.com/osrf/rocker/commit/6f8121f7b5c5aad379708ea468c01b97671af159) by Tully Foote).
- add coverage for extensions (#32) ([ac3afc5](https://github.com/osrf/rocker/commit/ac3afc5592771e45f866f22ba4357346f4353db4) by Tully Foote).
- adding a few basic unit tests (#30) ([ea951b7](https://github.com/osrf/rocker/commit/ea951b77cfaae6fd6921555779bfb195c748402e) by Tully Foote).
- Add codecov reports (#28) ([9ef5f36](https://github.com/osrf/rocker/commit/9ef5f361cdd94f1361a48c80deae48b5a58dea15) by Tully Foote).
- adding basic travis (#27) ([b538350](https://github.com/osrf/rocker/commit/b538350fcef5cc08eba4ad39a0911127270f9a20) by Tully Foote).
- Add unit tests for os_detection ([4b42a2d](https://github.com/osrf/rocker/commit/4b42a2de5d5dd9df7f8af6fed17c0080fdc4cbe8) by Tully Foote).
- add dependencies to backport script ([0df081e](https://github.com/osrf/rocker/commit/0df081efe22e8c4853c4bc1b942d7a2fe89aba9a) by Tully Foote).

### Fixed

- Fix empy stdout proxy logic for unit tests When the test runner changes std out for logging it breaks empy's stdout proxy logic. Fixes #9 ([0671e14](https://github.com/osrf/rocker/commit/0671e1429c0d54dba477bf475cae35252226c5f6) by Tully Foote).

## [0.1.3](https://github.com/osrf/rocker/releases/tag/0.1.3) - 2019-01-10

<small>[Compare with 0.1.2](https://github.com/osrf/rocker/compare/0.1.2...0.1.3)</small>

### Added

- add comment about python3-distro ([e28b546](https://github.com/osrf/rocker/commit/e28b54661dcd2c3fbc08f677d228c2ce7e649e3e) by Tully Foote).

### Fixed

- fix dependencies ([fafcab5](https://github.com/osrf/rocker/commit/fafcab54b24ec6cf0aa92b3adad3a16057717829) by Tully Foote).

## [0.1.2](https://github.com/osrf/rocker/releases/tag/0.1.2) - 2019-01-09

<small>[Compare with first commit](https://github.com/osrf/rocker/compare/abc236cbf234c8ac7bff30b865836aefb751dbef...0.1.2)</small>

### Added

- add command explicitly to argument parsing ([5e308a6](https://github.com/osrf/rocker/commit/5e308a61443c721f4a0de9129040f9898f538a04) by Tully Foote).
- Add tests for extensions ([50ac127](https://github.com/osrf/rocker/commit/50ac1278a488049ae6ce4325356151e24f4df4b7) by Tully Foote).
- add a few ignores core cleaner workspace diffs ([b498f03](https://github.com/osrf/rocker/commit/b498f031e50acff8c5e9d62c2e41365b289dd808) by Tully Foote).
- Add stdeb.cfg ([034abf1](https://github.com/osrf/rocker/commit/034abf1e41ed0ea0c6c5abf2703377257a660e24) by Tully Foote).
- add support for mounting devices, with a soft fail on not existing ([d3244ab](https://github.com/osrf/rocker/commit/d3244ab8f788bbc1e4355000e99176502d7f7d47) by Tully Foote).
- adding copyright headers ([601a156](https://github.com/osrf/rocker/commit/601a1561ccb8bbb2107e85a8afce14f623c12a04) by Tully Foote).
- Add extra arguments necessary for pulse Found here: https://github.com/jacknlliu/ros-docker-images/issues/7 Also fixed typo in the config. ([a9b6eba](https://github.com/osrf/rocker/commit/a9b6ebab3d09664ec2a014e67bd0ab83732326be) by Tully Foote).
- add to the wishlist ([6e224e2](https://github.com/osrf/rocker/commit/6e224e2435cedb74b3c42e727bd388190610f46b) by Tully Foote).
- add readme ([fa0d251](https://github.com/osrf/rocker/commit/fa0d251779bbf2add0842dcaefb40464451f3fd6) by Tully Foote).
- add a readme ([9d6bd66](https://github.com/osrf/rocker/commit/9d6bd6636d858e2b2bac3cb8ae74f683cad311b1) by Tully Foote).
- add parameter for disabling caching ([79a6beb](https://github.com/osrf/rocker/commit/79a6beb9301e0c446d9fe79d25d54067094c5c4d) by Tully Foote).

### Fixed

- fix assert spacing ([02601da](https://github.com/osrf/rocker/commit/02601da2fa9413192fa96df32cb65bf8a07cb9c6) by Tully Foote).
- fix network argument parsing ([d8b12af](https://github.com/osrf/rocker/commit/d8b12af21fe6ebf7bafdadf8e5f36e151ceb0ec6) by Tully Foote).
- fix docker API usage for pull ([a749985](https://github.com/osrf/rocker/commit/a749985104855bc44a5615eb8e25aa63833bd27a) by Tully Foote).

### Removed

- remove legacy test function ([4c1466a](https://github.com/osrf/rocker/commit/4c1466a217e4e150aa722836b3768abcd2efe425) by Tully Foote).
- remove legacy comments ([38b5903](https://github.com/osrf/rocker/commit/38b59034eb373ff12619529383dc8812446890ad) by Tully Foote).

