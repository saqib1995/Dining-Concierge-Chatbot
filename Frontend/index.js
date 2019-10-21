var chatHistory = [];

function sendMessageToApi(){
  var inputText = document.getElementById('user-input-message').value.trim().toLowerCase();
  document.getElementById('user-input-message').value = "";
  
  if(inputText == "") {
    return false;
  }else {
    chatHistory.push('<b><color = "red">User:</color> </b>' + inputText);
    document.getElementById('bot-response').innerHTML = "";
    chatHistory.forEach((element) => {
      document.getElementById('bot-response').innerHTML += "<p>" + element + "</p>";
    });
    receiveMessageFromApi(inputText);
    return false;
  }
}

function receiveMessageFromApi(inputText){

    var params = {};
    var body = {
      "message":inputText
    };

    var additionalParams = {
      headers: {},
      queryParams: {}
    };

    apigClient.chatbotPost(params,body,additionalParams).then((result) =>{

      console.log(result);
      chatHistory.push('<b><color = "Cyan">Bot:</color> </b>' + JSON.stringify(result.data));

      document.getElementById('bot-response').innerHTML = "";
      chatHistory.forEach((element) => {
        document.getElementById('bot-response').innerHTML += "<p>" +element + "</p>";
      });
  
  })
  .catch((err) =>{
    console.log(err);
  });

}