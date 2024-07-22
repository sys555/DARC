import Config

config :ain,
  ecto_repos: [DB.Repo]

config :ain, DB.Repo,
  database: "ain_repo",
  username: "postgres",
  password: "123456",
  hostname: "localhost",
  port: "5432"

config :faker, Faker,
  locale: :en
