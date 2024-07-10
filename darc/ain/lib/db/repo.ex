defmodule DB.Repo do
  use Ecto.Repo,
    otp_app: :ain,
    adapter: Ecto.Adapters.Postgres
end
