# Pastebin pack for stackstorm

This is definitely not something you want to use in production without checking every update... I expect a lot to change as I develop it.

There's a few main elements to it:

* Polling Sensor `pastebin.PasteBinPoller`
  * Routinely polls the [Pastebin scraping API endpoint](https://pastebin.com/doc_scraping_api) looking for new uploads.
  * It uses the kv store to keep a record of the most recently handled paste so you don't keep hitting old ones
  * Emits `pastebin.new_paste`
    * Payload is `key` and `date`
    * `key` is the 8 character string which refers to individual pastes
    * `date` is a seconds-since-unix-epoch-time timestamp of the paste
* Action `pastebin.scrape_paste_raw`
  * Give it the `key` and it'll grab the raw text of the paste
* Action `pastebin.scrape_paste_metadata`
  * Give it the `key` and it'll grab the metadata of the paste


## Usage

1. [Get a pastebin pro account](https://pastebin.com/pro) and whitelist your IP address [on the scraping API page](https://pastebin.com/doc_scraping_api).
2. Install the pack: `st2 pack install https://bitbucket.org/yaleman/st2-pastebin`
3. Configure a rule that uses the sensor/actions



