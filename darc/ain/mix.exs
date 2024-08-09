defmodule Ain.MixProject do
  use Mix.Project

  def project do
    [
      app: :ain,
      version: "0.1.0",
      elixir: "~> 1.15",
      start_permanent: Mix.env() == :prod,
      deps: deps(),
      elixir_opts: [erl_opts: "--erl \"-args_file ./vm.args\""]
    ]
  end

  # Run "mix help compile.app" to learn about applications.
  def application do
    [
      extra_applications: [:logger, :observer, :wx],
      mod: {Ain.Application, []}
    ]
  end

  # Run "mix help deps" to learn about dependencies.
  defp deps do
    [
      # {:dep_from_hexpm, "~> 0.3.0"},
      # {:dep_from_git, git: "https://github.com/elixir-lang/my_dep.git", tag: "0.1.0"}
      {:erlport, "~> 0.9"},
      {:jason, "~> 1.2"},
      {:recon, "~> 2.5"},
      {:ecto_sql, "~> 3.2"},
      {:postgrex, "~> 0.15"},
      {:ex_machina, "~> 2.7"},
      {:faker, "~> 0.17"},
      {:elixir_uuid, "~> 1.2"},
      {:mox, "~> 1.0", only: :test},
      {:grpc, "~> 0.9"},
      {:protobuf, "~> 0.11.0"},
      {:protobuf_generate, "~> 0.1.1"}
    ]
  end
end
