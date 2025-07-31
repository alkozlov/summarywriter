# Summary generation rules

## Summary generation rules for text

- Use simple and short sentences. They are easier to perceive and remember.
- Build the structure from simple to complex.
- If a CLI command is mentioned, be sure to show it with an explanation.
- Follow Markdown style guide.

## Summary generation rules for CLI commands

- make several versions of one cli command from simple to complex
- as the first example, use the minimum set of parameters required to execute the cli command
- then give more complex examples in ascending order of complexity
- give an explanation of the cli command arguments after its example. Use a table or list for this
- when writing cli command examples, try to stick to the practical bias of its application. For example, consider the cli command for creating Pods in Kubernetes. From a practical point of view, you often have to create Pods by forwarding a port when creating it. Or pass parameters through environment variables. Or combine this in one cli command. All these examples can be added to the notes as separate examples.
- be sure to describe the key parameters and arguments of the cli command. You can do this as a separate item.