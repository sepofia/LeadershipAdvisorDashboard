### Assumptions:
1. engagements.csv
 - `close_date` should be NaN if and only if the `status`='Open'|'On hold';
 - `lead_partner` is the responsible employee;
 - `fee_kEUR` counts as revenue, is unlocked when the engagement is closed;
2. milestones.csv
 - milestone process: "Kickoff" -> "Longlist" -> "Shortlist" -> "Offer" -> "Accepted"
 - 'manual review' in `notes` means adding candidates that haven't passed the previous milestones. But I didn't use this column.

### Data quality checks _(mentioned in the *Warning* block)_:
1. `status` is 'Opened'|'On hold', but `close_date` is not Null; _(filtered out from dataset)_
2. `status` is 'Closed', but `close_date` is Null;
3. `lead_partner` is Null;
4. `milestone_date` is Null. _(future plan)_

### Trade-offs:
1. Revenue per country: on map or bar chart. Map looks better in the final dashboard.
2. All analysis was performed ending on the _maximum date_ from the `start_date` and `close_date` columns.
3. Quarter timeframe is simply counted as the previous 3 months. But it would be better to count it according to the business quarters.
4. Initially I also produced a report for the weekly timeframe, but it was not very informative. So I switched to longer timeframes.

### Future plan:
1. **Build a proper time series for revenue:** compare to previous timeframe; align with business timeframes.
2. Take a look at the **revenue per engagement status**: to better understand how much revenue is frozen.
3. Check the **efficiency of lead partners**: also take a look at the _size_ and _level_ of their engagements.
4. _(additional data request):_ Check not only revenue, but also **margin**.
5. _(additional ML):_ Build a **forecasting model** that will allow us to predict the revenue.
