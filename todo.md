# Todo

- Basically I changed the <!form> in external_wearables.html so it incldues whatever statistics the user
  wants to observe when we fetch the data, such as sleep weight etc. Right now i only added two which are Steps and monitoring so i need to add the rest. Also i changed the form above to include also the start data. This needs to be written to the JSON file so update the endpoint to account for that.
- Then i need to determine how checkboxes send data. Is it a boolean or text? Whatever it is, i need to
  account for that by updating the Pydantic Model so that it now accounts for all of the statistics things and also the start date.
- I still havent completely figured out how the garmin thing works but i do know that in order to change the stats that the thing will fetch i need to modify the stats variable. Its the same 'stats' variable that is shown in the garmindb_cli.py file. Say the checkboxes are booleans. All the statistics that come back as True i need to add them to a list of Statistics classes. It should look something like this.

  [<Statistics.monitoring: 1>, <Statistics.steps: 2>, <Statistics.itime: 3>, <Statistics.sleep: 4>, <Statistics.rhr: 5>, <Statistics.hrv: 8>, <Statistics.weight: 6>, <Statistics.activities: 7>]

- Other than this, thats pretty much it. I need to actually understand the garmin api and how it fetches the data because ultimately what we want it to do is write the user data to external_user_data so that we can actually visualise the data which is a problem in itself but an easier one at least haha. Try and understand all the other command-line flags
