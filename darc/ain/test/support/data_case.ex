defmodule DB.DataCase do
  use ExUnit.CaseTemplate

  using do
    quote do
      alias DB.Repo

      import Ecto
      import Ecto.Changeset
      import Ecto.Query
      import DB.DataCase
    end
  end

  setup tags do
    :ok = Ecto.Adapters.SQL.Sandbox.checkout(DB.Repo)

    unless tags[:async] do
      Ecto.Adapters.SQL.Sandbox.mode(DB.Repo, {:shared, self()})
    end

    :ok
  end
end
