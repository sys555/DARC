# test/test_helper.exs
alias DB.Repo
ExUnit.start()
# Ensure the Repo is started before running tests
Repo.start_link()
Ecto.Adapters.SQL.Sandbox.mode(DB.Repo, :manual)
# Load support files
Enum.each(File.ls!("test/support"), fn file ->
  Code.require_file("support/#{file}", __DIR__)
end)
