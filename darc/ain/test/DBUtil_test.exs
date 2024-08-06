defmodule Util.DBUtilTest do
  use ExUnit.Case, async: true
  use DB.DataCase

  alias DB.Repo
  alias DB.Actor
  alias Util.DBUtil

  setup_all do
    :ok = Ecto.Adapters.SQL.Sandbox.checkout(DB.Repo)
    :ok
  end

  test "get_actor_with_uid/1 returns the actor with the given uid" do
    uid = Ecto.UUID.generate()
    actor = %Actor{
      uid: uid,
      name: "Test Actor",
      role: "Main Role",
      age: 30,
      graph_id: Ecto.UUID.generate()
    }
    {:ok, _} = Repo.insert(actor)

    result = DBUtil.get_actor_with_uid(uid)
    assert result.uid == uid
    assert result.name == "Test Actor"
    assert result.role == "Main Role"
    assert result.age == 30
  end

  test "get_actor_with_uid/1 returns nil if the actor does not exist" do
    uid = Ecto.UUID.generate()
    result = DBUtil.get_actor_with_uid(uid)
    assert result == nil
  end
end
