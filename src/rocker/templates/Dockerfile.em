TODO move logic here

{{ for p in prefixes }}

FROM {{base_image}}

{{ for s in snippets }}