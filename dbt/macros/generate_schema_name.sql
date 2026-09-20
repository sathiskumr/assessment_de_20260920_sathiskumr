{% macro generate_schema_name(custom_schema_name, node) -%}
    {#-
        dbt's default behaviour concatenates the target schema and the custom
        schema (e.g. public_staging). We want the literal schema names declared
        in dbt_project.yml (staging / marts), so override it.
    -#}
    {%- if custom_schema_name is none -%}
        {{ target.schema }}
    {%- else -%}
        {{ custom_schema_name | trim }}
    {%- endif -%}
{%- endmacro %}