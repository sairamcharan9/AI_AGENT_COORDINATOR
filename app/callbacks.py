def setup_before_agent_call(callback_context: CallbackContext):
    """Setup the agent with PostgreSQL database configuration."""

    # Setting up database settings in session.state
    if "database_settings" not in callback_context.state:
        db_settings = dict()
        db_settings["use_database"] = "PostgreSQL"
        callback_context.state["all_db_settings"] = db_settings

    # Setting up schema in instruction
    if callback_context.state["all_db_settings"]["use_database"] == "PostgreSQL":
        # Get PostgreSQL database settings
        callback_context.state["database_settings"] = get_postgres_database_settings()
        schema = callback_context.state["database_settings"]["pg_schema"]

        # Update the agent instruction with PostgreSQL schema information
        callback_context._invocation_context.agent.instruction = (
            prompt.PYTHON_AGENT_PROMPT
            + f"""

    --------- PostgreSQL Database Schema ---------
    {schema}

    When working with the database, use the PostgreSQL connection details provided.
    """
        )

