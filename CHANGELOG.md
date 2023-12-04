# Changelog

<!--next-version-placeholder-->

## v1.1.2 (2023-12-04)

### Fix

* Ensure stdout/stderr are written (flushed) before exiting ([`da8af45`](https://github.com/robinvandernoord/pydal2sql/commit/da8af450f45a963333076b726e5d6fc77d75f76d))
* Update db_type with None so postponed() error doesn't get raised ([`845aab3`](https://github.com/robinvandernoord/pydal2sql/commit/845aab3a30e061e669c4f5d3204b026c4ea793dd))
* Update db_type with None so postponed() error doesn't get raised ([`c353598`](https://github.com/robinvandernoord/pydal2sql/commit/c353598ca45d8d95e8c45a81a81b8ff1dbe0e4f6))

## v1.1.1 (2023-11-22)

### Fix

* **cli:** Some properties are not yet known before the cli args are parsed ([`a6909a2`](https://github.com/robinvandernoord/pydal2sql/commit/a6909a24df24acaef0fdc556a82e0986d7a0d9ed))
* Moved types to own file for re-use ([`e85228d`](https://github.com/robinvandernoord/pydal2sql/commit/e85228ddf2b69bebb55ab4b349d06b6ca57b8299))

## v1.1.0 (2023-11-20)

### Feature

* You can now add an 'input' to the pyproject to automatically select the db definition file ([`66b1fcc`](https://github.com/robinvandernoord/pydal2sql/commit/66b1fcc49f35c022deedb29b7c3505773fe23ed7))

## v1.0.1 (2023-11-20)

### Fix

* **config:** More config via toml and load dotenv even if config via toml ([`f077ce7`](https://github.com/robinvandernoord/pydal2sql/commit/f077ce7ecfc094d3851ff2d579dc6f7d3c8e4fcb))

## v1.0.0 (2023-11-17)

### Feature

* Allow --output-format and --output-file to create and alter ([`b3351a2`](https://github.com/robinvandernoord/pydal2sql/commit/b3351a292cb620d2c47ad503b116d8eca3e90115))
* Db_type from config toml ([`ad31040`](https://github.com/robinvandernoord/pydal2sql/commit/ad310404d6908f026e63ad3a9350abcb052aa8af))
* 'alter' via cli should work now! ([`a734a8c`](https://github.com/robinvandernoord/pydal2sql/commit/a734a8caccb2e89970faf71e581071e129a0564e))
* Changed @commit:file notation to file@commit for readability ([`f6abefe`](https://github.com/robinvandernoord/pydal2sql/commit/f6abefec8ffb32236efad141005085d371327f8e))
* Load file from disk, git or stdin for 'alter' ([`490dbe1`](https://github.com/robinvandernoord/pydal2sql/commit/490dbe1a816644b453f1acf3d07b087a4521ad95))
* Started on getting files from git for ALTER ([`075f2fd`](https://github.com/robinvandernoord/pydal2sql/commit/075f2fdd993969e0effe4846fe2055e9ae4b8444))
* Rewriting cli to Typer ([`673f208`](https://github.com/robinvandernoord/pydal2sql/commit/673f208e8d6b99af377a256c372315762e0a4597))
* Work in progress to support ALTER statements ([`f346073`](https://github.com/robinvandernoord/pydal2sql/commit/f34607373120bdba5be361d2f3dd8affe83300df))

### Fix

* Bump -core to at least 0.2.0 ([`f8de3b7`](https://github.com/robinvandernoord/pydal2sql/commit/f8de3b7c2fd03f24089c3ce6786cf70be99d7cc9))
* Update examples and tests to work with latest (dev) version of p2s-core ([`2d0a5db`](https://github.com/robinvandernoord/pydal2sql/commit/2d0a5dbbb3df2529630d8ba09a69ec8dd798f0d3))
* If define_table code is inside a function, --function can be added to specify this. `define_tables(db)` will be used by default. ([`6359e48`](https://github.com/robinvandernoord/pydal2sql/commit/6359e48e732c065399fd07301e1a7b33ac1741a3))
* Unknown and local imports in model file will be removed if they cause issues ([`2d3ae75`](https://github.com/robinvandernoord/pydal2sql/commit/2d3ae757b9c0b43886acc50aa724d4fe62dcbecb))
* Made 'create' work again with new cli ([`cf2f175`](https://github.com/robinvandernoord/pydal2sql/commit/cf2f175c074acb4eeec0be8e594d3a04ad0c9615))

### Breaking

* could change imports like `from pydal2sql.magic`!!! ([`a477b4d`](https://github.com/robinvandernoord/pydal2sql/commit/a477b4dc6a73264aa4b575e0855de00eee241d10))
* whole cli will change ([`673f208`](https://github.com/robinvandernoord/pydal2sql/commit/673f208e8d6b99af377a256c372315762e0a4597))

### Documentation

* Added more docstrings ([`1db78f4`](https://github.com/robinvandernoord/pydal2sql/commit/1db78f4aeab377ee514ed82124e0775ad3e2592f))
* Updated README with new cli options ([`7725ddd`](https://github.com/robinvandernoord/pydal2sql/commit/7725ddd8aaeef4c2644a2e64a10de15a40611a9e))
* Added todo's ([`609fa5f`](https://github.com/robinvandernoord/pydal2sql/commit/609fa5f2cf968321c6cdbf1ba7b0ecd232bc7298))

## v0.4.0 (2023-07-21)

### Feature

* **cli:** Use `tool.pydal2sql` in pyproject.toml to set default settings (which can normally be set with cli flags) ([`9c67f34`](https://github.com/robinvandernoord/pydal2sql/commit/9c67f3465a896f95c465ffcbeb51f90c84eb0291))

## v0.3.1 (2023-07-20)

### Documentation

* **readme:** Add another video ([`ce4312d`](https://github.com/robinvandernoord/pydal2sql/commit/ce4312deb4e9ef6b9261971214d88afc3c431345))

## v0.3.0 (2023-07-20)

### Feature

* 🪄✨ Add`--magic`™️ to the cli tooll! ([`b3f2409`](https://github.com/robinvandernoord/pydal2sql/commit/b3f24091a9201d60e392ac03a5360df35cdabc3e))

## v0.2.4 (2023-07-20)

### Docs

* doc(readme): added instruction ASCIInema

## v0.2.3 (2023-07-20)

### Fix

* Db type sometimes was an empty string, which is not
  None ([`d129cad`](https://github.com/robinvandernoord/pydal2sql/commit/d129cadacab0b8e5cef4799e6bff49c92d09731e))

## v0.2.2 (2023-07-20)

### Fix

* Moved rich from dev to actual
  dependencies ([`03409c0`](https://github.com/robinvandernoord/pydal2sql/commit/03409c04ab7b01f49870f863956578b12b3de968))

## v0.2.1 (2023-07-20)

### Fix

* Add dependency to
  rich ([`ffa8ef7`](https://github.com/robinvandernoord/pydal2sql/commit/ffa8ef7a23b3b02442e650a8be134356b6ef495c))

## v0.2.0 (2023-07-20)

### Feature

* Added simple cli where you can input some Python define_table statements and get CREATE TABLE SQL as
  output! ([`edc60c4`](https://github.com/robinvandernoord/pydal2sql/commit/edc60c46605e7f519c6fa8bf5c58f5fe9fe20531))

## v0.1.0 (2023-07-20)

### Feature

* Initial
  version ([`dfaef32`](https://github.com/robinvandernoord/pydal2sql/commit/dfaef324dcd68d2278be4bb47431a856314a143e))
