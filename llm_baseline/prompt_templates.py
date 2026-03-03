subtype_prompt = (
    "You are a linguistic analyst whose job is to select the subtype classification for a bridging anaphor - antecedent pair: mentions of newly introduced entities "
    "(the anaphor) in a text, for which a reader would need to refer back to a previously mentioned, non-identical entity (the antecedent) to resolve "
    "their meaning. There are several classes of bridging instances, defined by the associative relationship between the bridging anaphor and its associative antecedent. "
    "In the following subtype examples, the bridging antecedent is surrounded by *asterisks* and the bridging anaphor is surrounded by {{double curly brackets}}.\n\n"

    "comparison-relative: The anaphor is preceded by a comparative marker (other, another, same, more, ordinal modifiers, "
    "comparative adjectives, superlatives, etc.) which implies a comparison to the antecedent. For example: "
    "\"*The children* ... {{another child}} (=another with comparison to the aforementioned children); similar cases may be "
    "{{similar children}}, {{older children}} (compared to the aforementioned children), etc.\"\n"

    "comparison-sense: the semantic type of a phrase requires a previous mention to identify it, for example \"*the Italian "
    "restaurant* ... {{a Chinese one}}\" (we can't know \"a Chinese one\" is a restaurant without referring back to the Italian "
    "restaurant), or \"{{another one}}\", \"{{the others}}\" etc.\n"

    "comparison-time: the anaphor refers to a specific time/timeframe which is understandable with reference to the "
    "antecedent, for example: \"*Tuesday, February 2nd* ... {{the following week}}\"\n"

    "entity-meronomy: the anaphor is a subunit of the antecedent (part-whole), including physical subunits, portion-substance "
    "relations, and regions/subsections. For example: \"*the house* ... {{the door}}\" (=of the house).\n"

    "entity-associative: the anaphor is an attribute or closely associated entity of the antecedent, including both "
    "prototypical and inducible associations: \"*a wedding* ... {{the bride}}\" (=the bride at that wedding), implicit "
    "arguments of a predicate or a verbal nominalization: \"*a play*... {{the performance}}\" (=of the play), relational "
    "nouns: \"*a murder* ... {{the victim}}\""

    "entity-property: the anaphor is a physical or intangible property of the antecedent (e.g., smell, length, size, "
    "style, etc.): \"*the tea* ... {{the sweet aroma}}\"\n"

    "entity-resultative: the anaphor is logically inferable from the antecedent (e.g., result, "
    "transformation/transmutation, cause): \"*the dough* ... {{the bread}}\" (=the dough becomes bread after baking)"

    "set-member: the anaphor is an element of the antecedent set, including groups-member relations and "
    "classes-instances: \"*the cars* ... {{the Mazda}}\", additionally indefinite members to definite sets: \"*a candle* on "
    "each cupcake ... {{the candles}}\"\n"

    "set-subset: the anaphor is a subset of the antecedent set: \"*the cars* ... {{the Mazdas}}\" (not all Mazdas, just the "
    "subset among the aforementioned cars)\n"

    "set-span-interval: the anaphor is a sub-span of a spatial or temporal interval defined by the antecedent: \"*last "
    "week* ... {{Wednesday}}\" (=Wednesday of last week), \"*Sunday* ... {{the morning}} (=the morning portion of that Sunday)\"\n"

    "other: the anaphor requires a previous entity for interpretation, but it doesn't fit into any of the above categories. This is a rare class."

    "Here are 2 an examples of the task:\n"
    
    "In the following text, a bridging anaphora is marked with {{double curly brackets}} "
    "and the corresponding antecedent is surrounded by *asterisks*. Read the following text and for the bridging "
    "anaphor-antecedent pair, classify the variety of bridging subtype relation (defined above) that holds between the two entities. "
    "Multiple subtypes may apply to a single pair. Output a string of all applicable subtypes, connected by semicolons (no spaces). "
    "The possible subtype labels are as follows:\n"
    "comparison-relative\n"
    "comparison-sense\n"
    "comparison-time\n"
    "entity-associative\n"
    "entity-meronomy\n"
    "entity-property\n"
    "entity-resultative\n"
    "set-member\n"
    "set-subset\n"
    "set-span-interval\n"
    "other\n"
    "Antecedent Text:\n"
    "... with their friends to a picnic. The picnic was supposed to take place in *a grove*, but the shade wasn't enough, "
    "so they had to find a different place. Conny started to say ...\n"
    "Anaphor Text:\n"
    "... to a picnic. The picnic was supposed to take place in a grove, but {{the shade}} wasn't enough, "
    "so they had to find a different place. Conny started to say ...\n"
    "Answer:\n"
    "entity-associative\n"

    "In the following text, a bridging anaphora is marked with {{double curly brackets}} "
    "and the corresponding antecedent is surrounded by *asterisks*. Read the following text and for the bridging "
    "anaphor-antecedent pair, classify the variety of bridging subtype relation (defined above) that holds between the two entities. "
    "Multiple subtypes may apply to a single pair. Output a string of all applicable subtypes, connected by semicolons (no spaces). "
    "The possible subtype labels are as follows:\n"
    "comparison-relative\n"
    "comparison-sense\n"
    "comparison-time\n"
    "entity-associative\n"
    "entity-meronomy\n"
    "entity-property\n"
    "entity-resultative\n"
    "set-member\n"
    "set-subset\n"
    "set-span-interval\n"
    "other\n"
    "Antecedent Text:\n"
    "... this technique the basis of training for all types of dance . While dancing *ballet* takes dedication and "
    "requires serious training , you can learn the basics to prepare yourself for further study . Learn to get ready for practicing ...\n"
    "Anaphor Text:\n"
    "... making this technique the basis of training for all types of dance . While dancing ballet takes dedication and "
    "requires serious training , you can learn the basics to prepare yourself for {{further study}} . Learn to get ready for ...\n"
    "Answer:\n"
    "comparison-relative\n"

    "In the following text, a bridging anaphora is marked with {{double curly brackets}} "
    "and the corresponding antecedent is surrounded by *asterisks*. Read the following text and for the bridging "
    "anaphor-antecedent pair, classify the variety of bridging subtype relation (defined above) that holds between the two entities. "
    "Multiple subtypes may apply to a single pair. Output a string of all applicable subtypes, connected by semicolons (no spaces). "
    "The possible subtype labels are as follows:\n"
    "comparison-relative\n"
    "comparison-sense\n"
    "comparison-time\n"
    "entity-associative\n"
    "entity-meronomy\n"
    "entity-property\n"
    "entity-resultative\n"
    "set-member\n"
    "set-subset\n"
    "set-span-interval\n"
    "other\n"
    "Antecedent Text:\n"
    "... {antecedent_text} ...\n"
    "Anaphor Text:\n"
    "... {anaphor_text} ...\n"
    "Answer:\n"
)

bridge_antec_prompt = (
    "You are a linguistic analyst whose job is to select the associative antecedent for of a bridging anaphor: mentions of newly introduced entities "
    "(noun phrases) in a text, for which a reader would need to refer back to a previously mentioned, non-identical entity (the antecedent) to resolve "
    "their meaning. There are several classes of bridging instances, defined by the associative relationship between the bridging anaphor and its associative antecedent. "
    "In the following examples, the bridging antecedent is surrounded by *asterisks* and the bridging anaphor is surrounded by {{double curly brackets}}.\n\n"

    "comparison-relative: The anaphor is preceded by a comparative marker (other, another, same, more, ordinal modifiers, "
    "comparative adjectives, superlatives, etc.) which implies a comparison to the antecedent. For example: "
    "\"*The children* ... {{another child}} (=another with comparison to the aforementioned children); similar cases may be "
    "{{similar children}}, {{older children}} (compared to the aforementioned children), etc.\"\n"

    "comparison-sense: the semantic type of a phrase requires a previous mention to identify it, for example \"*the Italian "
    "restaurant* ... {{a Chinese one}}\" (we can't know \"a Chinese one\" is a restaurant without referring back to the Italian "
    "restaurant), or \"{{another one}}\", \"{{the others}}\" etc.\n"

    "comparison-time: the anaphor refers to a specific time/timeframe which is understandable with reference to the "
    "antecedent, for example: \"*Tuesday, February 2nd* ... {{the following week}}\"\n"

    "entity-meronomy: the anaphor is a subunit of the antecedent (part-whole), including physical subunits, portion-substance "
    "relations, and regions/subsections. For example: \"*the house* ... {{the door}}\" (=of the house).\n"

    "entity-associative: the anaphor is an attribute or closely associated entity of the antecedent, including both "
    "prototypical and inducible associations: \"*a wedding* ... {{the bride}}\" (=the bride at that wedding), implicit "
    "arguments of a predicate or a verbal nominalization: \"*a play*... {{the performance}}\" (=of the play), relational "
    "nouns: \"*a murder* ... {{the victim}}\""

    "entity-property: the anaphor is a physical or intangible property of the antecedent (e.g., smell, length, size, "
    "style, etc.): \"*the tea* ... {{the sweet aroma}}\"\n"

    "entity-resultative: the anaphor is logically inferable from the antecedent (e.g., result, "
    "transformation/transmutation, cause): \"*the dough* ... {{the bread}}\" (=the dough becomes bread after baking)"

    "set-member: the anaphor is an element of the antecedent set, including groups-member relations and "
    "classes-instances: \"*the cars* ... {{the Mazda}}\", additionally indefinite members to definite sets: \"*a candle* on "
    "each cupcake ... {{the candles}}\"\n"

    "set-subset: the anaphor is a subset of the antecedent set: \"*the cars* ... {{the Mazdas}}\" (not all Mazdas, just the "
    "subset among the aforementioned cars)\n"

    "set-span-interval: the anaphor is a sub-span of a spatial or temporal interval defined by the antecedent: \"*last "
    "week* ... {{Wednesday}}\" (=Wednesday of last week), \"*Sunday* ... {{the morning}} (=the morning portion of that Sunday)\"\n"

    "other: the anaphor requires a previous entity for interpretation, but it doesn't fit into any of the above categories. This is a rare class."

    "Here are 2 an examples of the task:\n"

    "Please return a single string for associative antecedent of the bridging anaphor surrounded by {{double curly brackets}}. Output the antecedent mention phrase exactly as it "
    "appears in the text. If there is no associative antecedent, return \"no antecedent\". The antecedent you are returning CANNOT be the same as the bracketed anaphor.\n"
    "Text:\n"
    "... with their friends to a picnic. The picnic was supposed to take place in a grove, but {{the shade}} wasn't enough, "
    "so they had to find a different place. Conny started to say ...\n"
    "Answer:\n"
    "a grove\n"

    "Please return a single string for associative antecedent of the bridging anaphor surrounded by {{double curly brackets}}. Output the antecedent mention phrase exactly as it "
    "appears in the text. If there is no associative antecedent, return \"no antecedent\".\n"
    "Text:\n"
    "... making this technique the basis of training for all types of dance . While dancing ballet takes dedication and "
    "requires serious training , you can learn the basics to prepare yourself for {{further study}} . Learn to get ready for practicing ...\n"
    "Answer:\n"
    "ballet\n"

    "Please return a single string for associative antecedent of the bridging anaphor surrounded by {{double curly brackets}}. Output the antecedent mention phrase exactly as it "
    "appears in the text. If there is no associative antecedent, return \"no antecedent\".\n"
    "Text:\n"
    "{text}\n"
    "Answer:\n"
)

bridge_ana_prompt = (
    "You are a linguistic analyst whose job is to find cases of bridging anaphora: mentions of newly introduced entities "
    "(noun phrases) in a text, for which a reader would need to refer back to a previously mentioned, non-identical entity to resolve "
    "their meaning. There are several classes of bridging anaphors, any of which should be identified in the text being "
    "analyzed. In the following examples, the bridging anaphor is surrounded by *asterisks*.\n\n"
    
    "comparison-relative: The anaphor is preceded by a comparative marker (other, another, same, more, ordinal modifiers, "
    "comparative adjectives, superlatives, etc.) which implies a comparison to the antecedent. For example: "
    "\"The children... *another child* (=another with comparison to the aforementioned children); similar cases may be "
    "*similar children*, *older children* (compared to the aforementioned children), etc.\"\n"
    
    "comparison-sense: the semantic type of a phrase requires a previous mention to identify it, for example \"the Italian "
    "restaurant... *a Chinese one*\" (we can't know \"a Chinese one\" is a restaurant without referring back to the Italian "
    "restaurant), or \"*another one*\", \"*the others*\" etc.\n"
    
    "comparison-time: the anaphor refers to a specific time/timeframe which is understandable with reference to the "
    "antecedent, for example: \"Tuesday, February 2nd ... *the following week*\"\n"
    
    "entity-meronomy: the anaphor is a subunit of the antecedent (part-whole), including physical subunits, portion-substance "
    "relations, and regions/subsections. For example: \"the house ... *the door*\" (=of the house).\n" 
    
    "entity-associative: the anaphor is an attribute or closely associated entity of the antecedent, including both "
    "prototypical and inducible associations: \"a wedding ... *the bride*\" (=the bride at that wedding), implicit "
    "arguments of a predicate or a verbal nominalization: \"a play... *the performance*\" (=of the play), relational "
    "nouns: \"a murder ... *the victim*\""
    
    "entity-property: the anaphor is a physical or intangible property of the antecedent (e.g., smell, length, size, "
    "style, etc.): \"the tea... *the sweet aroma*\"\n"
    
    "entity-resultative: the anaphor is logically inferable from the antecedent (e.g., result, "
    "transformation/transmutation, cause): \"the dough ... *the bread*\" (=the dough becomes bread after baking)"
    
    "set-member: the anaphor is an element of the antecedent set, including groups-member relations and "
    "classes-instances: \"the cars ... *the Mazda*\", additionally indefinite members to definite sets: \"a candle on "
    "each cupcake... *the candles*\"\n"
    
    "set-subset: the anaphor is a subset of the antecedent set: \"the cars ... *the Mazdas*\" (not all Mazdas, just the "
    "subset among the aforementioned cars)\n"

    "set-span-interval: the anaphor is a sub-span of a spatial or temporal interval defined by the antecedent: \"last "
    "week... *Wednesday*\" (=Wednesday of last week), \"Sunday... *the morning* (=the morning portion of that Sunday)\"\n"
    
    "other: the anaphor requires a previous entity for interpretation, but it doesn't fit into any of the above categories. This is a rare class."
    
    "There are also some exceptions which should NOT be identified as bridging anaphora:\n"
    
    "Coreference: If an entity has a previous mention, it cannot be an instance of bridging. For instance, in \"Catherine and Henry had their wedding last week. The bride was very beautiful\", even though there is an associative relationship between the wedding and the bride, since \"the bride\" corefers with \"Catherine\", which has already been introduced to the discourse, \"the bride\" is not eligible to be an instance of bridging.\n"
    
    "Bridging-contained: If the entity one would need to refer back to in order to understand the bridging anaphor is a direct modifier in the noun phrase of the potential bridging anaphor, e.g. \"the focus of the story\" or \"two of them\", it should not be annotated as bridging. In other words, the previous antecedent entity must be outside of the nominal phrase containing the anaphor. An entity that is followed by a prepositional phrase or a relative clause is sufficiently qualified and is thus NOT an instance of bridging.\n"
    
    "Generics/Situational bridging: Entities that are accessible due to general world knowledge or situational context are not considered instances of bridging, i.e., if it doesn’t have a previous associated antecedent entity to be bridging from, it cannot be bridging.\n"
    
    "Possession with an explicit possessive: If the potential bridging anaphor contains an explicit possessive which corefers with the associative antecedent entity, no bridging relation is necessary. Explicit coreference between the associative antecedent and the possessive is sufficient (e.g., [Mark]…[his] house → no bridging, coreference between \"Mark\" and \"his\"). Contrast this with [the family] … *the house* → bridging, since we cannot interpret which house it is (the house of the family) without referring to \"the family\", which is outside of the anaphor phrase.\n"
    
    "Here are 2 an examples of the task:\n"
    
    "Please return a list all of the bridging anaphors in the following text in the order in which they appear. Output the anaphor mention phrase exactly as it "
    "appears in the text. If there are no bridging anaphors, return an empty list.\n"
    "Text:\n"
    "... with their friends to a picnic. The picnic was supposed to take place in a grove, but the shade wasn't enough, "
    "so they had to find a different place. Conny started to say ...\n"
    "Answer(s):\n"
    "[\"the shade\", \"a different place\"]\n"
    
    "Please return a list all of the bridging anaphors in the following text in the order in which they appear. Output the anaphor mention phrase exactly as it "
    "appears in the text. If there are no bridging anaphors, return an empty list.\n"
    "Text:\n"
    "... making this technique the basis of training for all types of dance . While dancing ballet takes dedication and "
    "requires serious training , you can learn the basics to prepare yourself for further study . Learn to get ready for practicing...\n"
    "Answer(s):\n"
    "[\"the basics\", \"further study\"]\n"
    
    "Please return a list all of the bridging anaphors in the following text in the order in which they appear. Output the anaphor mention phrase exactly as it "
    "appears in the text. If there are no bridging anaphors, return an empty list.\n"
    "Text:\n"
    "{text}\n"
    "Answer(s):\n"
)