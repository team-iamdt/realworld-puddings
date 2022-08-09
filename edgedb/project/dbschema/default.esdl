module default {
  # Base Model for Define Essential Values
  abstract type BaseModel {
    overloaded required property id -> uuid {
      constraint exclusive;
      readonly := true;
      default := uuid_generate_v1mc();
    };

    required property created_at -> datetime;
    required property updated_at -> datetime;
    property deleted_at -> datetime;
    required property deleted -> bool {
      default := false;
    };

    # On Update / Create Hook is still not supported.
    # Reference: https://github.com/edgedb/edgedb/discussions/3180

    # rule bump_updated_at on update {
    #   update BaseModel set {
    #     updated_at := datetime_current();
    #   };
    # };

    # rule initialize_on_creation on create {
    #   update BaseModel set {
    #     created_at := datetime_current();
    #     updated_at := datetime_current();
    #   };
    # };

    index on (.created_at) {
      annotation title := "CreatedAt Index";
    };
  }

  # Define User Model
  type User extending BaseModel {
    # Email is unique.
    required property email -> str {
      constraint exclusive;
    };

    required property password -> str;

    required property name -> str {
      constraint min_len_value(3);
    };

    index on (.email) {
      annotation title := "Email Index";
    };
  }

  abstract link IdIndex {
    property id -> uuid;

    # It can makes migration fail, Reference: https://github.com/edgedb/edgedb/issues/4237
    # index on (__subject__@id);
  }

  # Define Memo and Comment Model
  type Memo extending BaseModel {
    required link created_by extending IdIndex -> User;
    multi link accessable_users extending IdIndex -> User;

    required property title -> str;
    required property content -> str;
    required property tags -> array<str> {
      default := <array<str>>[];
    };

    # global variables cannot be accessed in indexed fields.
    # so I decided to disable using access policy.

    # access policy owner
    #   allow all
    #   using (global current_user_id ?= .created_by.id);

    # access policy accessable
    #   allow select
    #   using ((global current_user_id in .accessable_users.id) ?? false);
  }

  type Comment extending BaseModel {
    required link created_by extending IdIndex -> User;
    required link memo extending IdIndex -> Memo;
    required property content -> str;

    # global variables cannot be accessed in indexed fields.
    # so I decided to disable using access policy.

    # access policy owner
    #   allow all
    #   using (global current_user_id ?= .created_by.id);

    # access policy accessable
    #   allow select
    #   using ((global current_user_id in .memo.accessable_users.id) or ((global current_user_id ?= .memo.created_by.id) ?? false));
  }
}
