# Changelog

## [2.1.1](https://github.com/ooliver1/mafic/compare/v2.1.0...v2.1.1) (2023-04-30)


### Bug Fixes

* **node:** urlencode query ([#66](https://github.com/ooliver1/mafic/issues/66)) ([f31ff5e](https://github.com/ooliver1/mafic/commit/f31ff5e8ddd2bbe728f9b4a61a4b5fb88ababcad))


### Documentation

* **filter:** gemerate ([bb17994](https://github.com/ooliver1/mafic/commit/bb17994f2642dc9d627fb2d4e43ffc16a1cb32c6))

## [2.1.0](https://github.com/ooliver1/mafic/compare/v2.0.1...v2.1.0) (2023-04-19)


### Features

* **filter:** allow more types for Equalizer ([#61](https://github.com/ooliver1/mafic/issues/61)) ([a3d2596](https://github.com/ooliver1/mafic/commit/a3d2596eab8223dca94174ab4977e97b25ed5b3b))
* **player:** add has_filter method ([#63](https://github.com/ooliver1/mafic/issues/63)) ([bda2301](https://github.com/ooliver1/mafic/commit/bda230188a9a2f5c39effa8e26093c0484f652ed))

## [2.0.1](https://github.com/ooliver1/mafic/compare/v2.0.0...v2.0.1) (2023-02-17)


### Bug Fixes

* **node:** literally blind ([01c34d9](https://github.com/ooliver1/mafic/commit/01c34d9d7615e44d2ce955194d97feb47a0b73b8))

## [2.0.0](https://github.com/ooliver1/mafic/compare/v1.2.1...v2.0.0) (2023-02-17)


### ⚠ BREAKING CHANGES

* players is now a read-only list property

### Features

* properly resume players even on full restart ([#53](https://github.com/ooliver1/mafic/issues/53)) ([e3d7ba5](https://github.com/ooliver1/mafic/commit/e3d7ba517319011bd9452b9d9dcc74a6b396a8c7))


### Bug Fixes

* **node:** ignore no content responses ([#54](https://github.com/ooliver1/mafic/issues/54)) ([8a13874](https://github.com/ooliver1/mafic/commit/8a138743aadbc74a370ee3218b1a81d8cbe8001b))
* **player:** set blank filter if no filters enabled ([#51](https://github.com/ooliver1/mafic/issues/51)) ([8ccf60e](https://github.com/ooliver1/mafic/commit/8ccf60e2c6b3cd45b4b74d641810152e7c8bb553))

## [1.2.1](https://github.com/ooliver1/mafic/compare/v1.2.0...v1.2.1) (2023-02-16)


### Bug Fixes

* **player:** fix player position being wildly out ([#49](https://github.com/ooliver1/mafic/issues/49)) ([63124b8](https://github.com/ooliver1/mafic/commit/63124b878f55fe25a30bdfaa9ccbf5b63ecda98b))


### Miscellaneous Chores

* release 1.2.1 ([41e9a49](https://github.com/ooliver1/mafic/commit/41e9a4923a49b7a8af0eda30c4c6a2269d28bdf5))
* release 1.2.1 ([1ac48d4](https://github.com/ooliver1/mafic/commit/1ac48d4d5ae67cec86a525fd246afac3d5d55450))

## [1.2.0](https://github.com/ooliver1/mafic/compare/v1.1.1...v1.2.0) (2023-02-16)


### Features

* **player:** expose Player.paused ([#44](https://github.com/ooliver1/mafic/issues/44)) ([6e25025](https://github.com/ooliver1/mafic/commit/6e2502505f96bb98d2b7be2c63425156a211ed5d))


### Bug Fixes

* **node:** stop appending /v3 if done already ([#42](https://github.com/ooliver1/mafic/issues/42)) ([00d547c](https://github.com/ooliver1/mafic/commit/00d547c697849a792e264931086630eff95c83b3))
* **pool:** ignore unavailable nodes ([#45](https://github.com/ooliver1/mafic/issues/45)) ([f2d6b22](https://github.com/ooliver1/mafic/commit/f2d6b2282d3f03c8ac6be076ce35eb5c0d97c1c5))

## [1.1.1](https://github.com/ooliver1/mafic/compare/v1.1.0...v1.1.1) (2023-02-15)


### Bug Fixes

* **libraries:** use TYPE_CHECKING to resolve import loop in disnake ([#40](https://github.com/ooliver1/mafic/issues/40)) ([b44a16b](https://github.com/ooliver1/mafic/commit/b44a16b2c551ab51bdc3dac3466b1743f0944ed3))

## [1.1.0](https://github.com/ooliver1/mafic/compare/v1.0.3...v1.1.0) (2023-02-12)


### Features

* allow players to not be disconnected by library ([283485d](https://github.com/ooliver1/mafic/commit/283485df6fa8722266e5d72001a1e3a108d42195))

## [1.0.3](https://github.com/ooliver1/mafic/compare/v1.0.2...v1.0.3) (2023-02-12)


### Bug Fixes

* check major version at runtime ([547b4b4](https://github.com/ooliver1/mafic/commit/547b4b47edbfa3b9e9e2dd36512d94a000bb7ecf))

## [1.0.2](https://github.com/ooliver1/mafic/compare/v1.0.1...v1.0.2) (2023-02-11)


### Bug Fixes

* **player:** resolve issue with player.stop being ignored ([eacab59](https://github.com/ooliver1/mafic/commit/eacab5903da15f9f3339be7ee581c4f5353a12b2))

## [1.0.1](https://github.com/ooliver1/mafic/compare/v1.0.0...v1.0.1) (2023-02-07)


### Miscellaneous Chores

* update project status ([2eff4c3](https://github.com/ooliver1/mafic/commit/2eff4c3e2e85b8946679b6ce8cdac39da7620b8b))

## [1.0.0](https://github.com/ooliver1/mafic/compare/v0.3.0...v1.0.0) (2023-02-07)


### Features

* make events generic on player ([68868e0](https://github.com/ooliver1/mafic/commit/68868e0b54560f7dfea901de30bfcbdbad69f779))


### Bug Fixes

* **node:** stringify bool query params for `replace` ([63b7462](https://github.com/ooliver1/mafic/commit/63b746243c84f9a28cdd126369ffdb91a85581bf))


### Miscellaneous Chores

* update readme ([5763b4a](https://github.com/ooliver1/mafic/commit/5763b4a6df7b64ef5bb4e50718c44d90d018c964))

## [0.3.0](https://github.com/ooliver1/mafic/compare/v0.2.0...v0.3.0) (2023-02-04)


### Features

* add event dispatching ([#28](https://github.com/ooliver1/mafic/issues/28)) ([d4a837f](https://github.com/ooliver1/mafic/commit/d4a837f9592d16194ac50fe82329809b615a6697))
* add fine grained errors raised from http operations ([#30](https://github.com/ooliver1/mafic/issues/30)) ([b1f4042](https://github.com/ooliver1/mafic/commit/b1f4042879039f18a8636aaa78a7c16afb8e3858))
* support plugin search types ([#31](https://github.com/ooliver1/mafic/issues/31)) ([1985484](https://github.com/ooliver1/mafic/commit/19854842b7b1864718e2dc43a0b94d0ea450cd2f))


### Bug Fixes

* **node:** improve version checking ([736c268](https://github.com/ooliver1/mafic/commit/736c268a51e2805efef2d4be1f4c9312efb7b01d))
* **node:** properly resume ([bb20ad6](https://github.com/ooliver1/mafic/commit/bb20ad6cc5ab4122178a00e603525039a9b7f259))
* **node:** send auth for version, lol ([29baebf](https://github.com/ooliver1/mafic/commit/29baebf0d8d8d244ac19d713642fb99452c3a528))
* **node:** use track id not identifier to play ([12e0db4](https://github.com/ooliver1/mafic/commit/12e0db499a07a2a56a804d817cfdcec2dba43857))
* **stats:** framestats is actually ommitable ([4c96b70](https://github.com/ooliver1/mafic/commit/4c96b70da5f34931207064a8e8a2522d3b71af8b))


### Documentation

* add documentation ([#25](https://github.com/ooliver1/mafic/issues/25)) ([8f8a421](https://github.com/ooliver1/mafic/commit/8f8a421df1f2143f136de3196ff561fb371d5307))
* add events ([3bc39f4](https://github.com/ooliver1/mafic/commit/3bc39f412a68a56b3e4d668c7fd8df72b4e6b58b))
* export ignore lib check env var ([f2f04eb](https://github.com/ooliver1/mafic/commit/f2f04eb0e9a0646853f0d2b066bca2faa7076f05))
* improve front page ([49d087d](https://github.com/ooliver1/mafic/commit/49d087d202ba682b9252ef7bb30e8a1981f74b29))
* **installing:** fix typo ([68c1c60](https://github.com/ooliver1/mafic/commit/68c1c601b934fe25fcd3f89f91c2d38f6ca7552a))

## [0.2.0](https://github.com/ooliver1/mafic/compare/v0.1.0...v0.2.0) (2022-11-09)


### Features

* add mafic -v for version checking ([#5](https://github.com/ooliver1/mafic/issues/5)) ([3dbf5ab](https://github.com/ooliver1/mafic/commit/3dbf5abfac4753e6ecb7488a83dd2ab13c87b382))
* add node selection/balancing ([#18](https://github.com/ooliver1/mafic/issues/18)) ([f5fc457](https://github.com/ooliver1/mafic/commit/f5fc457cf8274d4ace042e7cbf4342949ceaf7a7))


### Reverts

* "ci: ignore test bot from snyk analysis" ([92c7482](https://github.com/ooliver1/mafic/commit/92c74820b04a0271f4ff81253f3844471c6bd1c2))


### Documentation

* add documentation for contributing ([#6](https://github.com/ooliver1/mafic/issues/6)) ([81fde97](https://github.com/ooliver1/mafic/commit/81fde97b32296d109968142fdc13535e6cd56da9))
* **contributing:** use level 3 headers for commits ([452edf2](https://github.com/ooliver1/mafic/commit/452edf27673f2a5f21cb5b5713fff8f1a6862ac4))
* **contributing:** what a shambles ([c4be211](https://github.com/ooliver1/mafic/commit/c4be2110c70f0946f6cefab4be5e49b41a1cc0fd))
* **readme:** add fancy new shields.io badges ([#2](https://github.com/ooliver1/mafic/issues/2)) ([1af8fa1](https://github.com/ooliver1/mafic/commit/1af8fa1f955e0ad307acc0d36838b9fabaf20603))

## 0.1.0 (2022-10-25)


### Features

* absolutely flood with logging calls ([68621aa](https://github.com/ooliver1/mafic/commit/68621aa5f3801304bd2b0e81c1df7f2bc024ebca))
* add basic init file ([4475195](https://github.com/ooliver1/mafic/commit/4475195f6e0c6f80a31f5757d3f6685ba21faf11))
* add blank player class ([8f7c0f9](https://github.com/ooliver1/mafic/commit/8f7c0f9c50d5a9b7b5ecffc219672005997ad7e5))
* add decoder for lavaplayer's weird syntax ([7165906](https://github.com/ooliver1/mafic/commit/716590655e7b05531c361830ab0ec565caa2065c))
* add ip address support ([fe70c2b](https://github.com/ooliver1/mafic/commit/fe70c2b3951b35bae5f1c354fcaeaf33ddc3abcb))
* add management of multiple libraries ([5c2072d](https://github.com/ooliver1/mafic/commit/5c2072d519942474445db741c3acd8dcacff94bf))
* add player controls ([5aead6a](https://github.com/ooliver1/mafic/commit/5aead6aec6e19eda3e46bfbb6d233fffb435d025))
* add playlists ([7b5e9e1](https://github.com/ooliver1/mafic/commit/7b5e9e1e4fc264b1790bcfdb7ca910a78ff56b29))
* add plugin endpoints ([abbb893](https://github.com/ooliver1/mafic/commit/abbb8932da221b7e47308264c4b4425cc4f886e0))
* add stats support ([b991b3d](https://github.com/ooliver1/mafic/commit/b991b3d507433d73ec5d1668997c1b583f1a6baf))
* add track decoding ([278d1d0](https://github.com/ooliver1/mafic/commit/278d1d0b11de407bfa92c1192d0706a051afe363))
* begin filters ([036fa65](https://github.com/ooliver1/mafic/commit/036fa65909da970aad377f5e114ac7450696ef73))
* handle connecting and disconnecting properly ([38ea309](https://github.com/ooliver1/mafic/commit/38ea3095c2d03b992c1c0831de404e78cb7a8f2c))
* initial commit, as im not gonna stop if i dont commit ([fd3b219](https://github.com/ooliver1/mafic/commit/fd3b219943df16caa0b08df5ff49f69a1735661a))
* make Player.position length aware ([f838968](https://github.com/ooliver1/mafic/commit/f838968e903b8dbe11af7c974b3d98a7357763fc))
* **node:** add most ws wrappers ([b6edd13](https://github.com/ooliver1/mafic/commit/b6edd131dcb115e54c855a0b0c25c6c76b228934))
* **node:** add play route ([8a12d6e](https://github.com/ooliver1/mafic/commit/8a12d6ebee9e36d0c9f5023dadb61b324d59d138))
* support getting tracks ([d096e4e](https://github.com/ooliver1/mafic/commit/d096e4eb118138abf5691d7058fb35647d380878))
* support incoming messages ([9c71b66](https://github.com/ooliver1/mafic/commit/9c71b667149aa4545d448427bd5d161f410baccc))
* support resuming ([c9486d8](https://github.com/ooliver1/mafic/commit/c9486d84ceb137e664426c72826eb798e91766d2))
* update state of players ([6bce46e](https://github.com/ooliver1/mafic/commit/6bce46ed86aa78b9528902884db7bb27176b8fc1))


### Bug Fixes

* make thing do work ([113b37a](https://github.com/ooliver1/mafic/commit/113b37ad6bda173c4e5cc68c4d779a4dc802ff12))
* **playlists:** use classmethod instead of init ([861e050](https://github.com/ooliver1/mafic/commit/861e0501659351171d1dab339cf4012e8a3b3f20))
* remove accidental file commit ([198cdd0](https://github.com/ooliver1/mafic/commit/198cdd0ea8fef11c672c87ad96622e866ba0f68a))
* resolve pyright issues ([ee908b2](https://github.com/ooliver1/mafic/commit/ee908b2bf2d2fb13c3568d0c9783b3d672de0cc5))


### Documentation

* add basic readme ([19e8606](https://github.com/ooliver1/mafic/commit/19e8606bf180f83e46b417a2010cd46bec27cd40))
