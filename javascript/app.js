const { Configuration, OpenAIApi } = require("openai");

const express = require("express");
const bodyParser = require("body-parser");
require("dotenv").config();

const app = express();
const port = process.env.PORT || 3000;

app.use(bodyParser.urlencoded({ extended: false }));
app.use(bodyParser.json());
app.use(express.static("public"));

const configuration = new Configuration({
  apiKey: process.env.OPENAIAPI_KEY,
});

const openai = new OpenAIApi(configuration);

const getResponse = async (issues, concerns) => {
  console.log(process.env.OPENAIAPI_KEY, "this is the ai key");
  const response = await openai
    .createChatCompletion({
      model: "gpt-3.5-turbo",
      max_tokens: 150,
      messages: [
        {
          role: "user",
          content: `You will help write a letter to a person's MLA. This is the issue they're dealing with: "${issues}" and this is why it is concerning to them: "${concerns}"`,
        },
      ],
    })
    .catch((err) => console.log(err.response));
  return response;
};

app.get("/", (req, res) => {
  res.render("index.ejs");
});

app.post("/writeletter", async (req, res) => {
  const { issues, concerns } = req.body;
  // const issues = req.body.issues;
  // const concerns = req.body.concerns;

  const response = await getResponse(issues, concerns);
  console.log(response.data.choices[0].message.content);
  const formattedResponse = formatResponse(response, issues, concerns);
  res.send(formattedResponse);
});

const formatResponse = (response, issues, concerns) => {
  if (
    !response ||
    !response.data ||
    !response.data.choices ||
    response.data.choices.length === 0
  ) {
    return res.render("error", { error: "No response from OpenAI" });
  }
  const message = response.data.choices[0].message.content.replace(
    /\n/g,
    "</p><p>"
  );
  return `<html>${headHTML}<body><h1>Here is your letter: </h1><p>${message}</p></body></html>`;
};

app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});
