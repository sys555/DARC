import Config

config :ain,
  ecto_repos: [DB.Repo]

config :ain, DB.Repo,
  database: "ain_repo",
  username: "postgres",
  password: "123456",
  hostname: "localhost",
  port: "5432",
  ownership_timeout: 60_000_000,     # DB connection time; 1_000 mins;
  pool: Ecto.Adapters.SQL.Sandbox

config :faker, Faker,
  locale: :en
