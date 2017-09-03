Big picture todo:

- [ ] Add error checking - if error encountered then log it, update leagues.csv to skip it (after X times?), and send pushover notification
- [ ] Expand leagues.csv - league_name; error
- [ ] Improve leagues.csv - check for error previous time; if error, skip (or if X errors in a row, then skip)
- [ ] League name - get it from leagues.csv; if empty, scrape for it and update leagues.csv

Errors to check:

- [ ] League not public
- [ ] Pushover error (not 200)
- [ ] Other issues - can't scrape table, can't format scrape into text, etc.

If errors happen:

- [ ] Update leagues.csv to include 1 for error (to skip next time - check for this)
- [ ] Log it to errors.log
- [ ] Send different pushover notification (error notification function?)

leagues.csv processing:

- [ ] Add league_name field as column 5 (default = blank; if not blank, use it; if blank, fill it (get_league_name function?)
- [ ] Add error field as column 6 (0 = default = no error; 1 = error in processing = skip next time; make this integer?  e.g. skip after 5 errors?)
