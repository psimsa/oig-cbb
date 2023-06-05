using System.Net.Http.Headers;
using System.Text.Json;

var email = args[0];
var password = args[1];

var loginCommand = new { email, password };

var client = new HttpClient();
client.BaseAddress = new Uri("https://www.oigpower.cz/cez/");

// Login
HttpContent content = new StringContent(JsonSerializer.Serialize(loginCommand));
content.Headers.ContentType = new MediaTypeHeaderValue("application/json");
var message = new HttpRequestMessage(HttpMethod.Post, "inc/php/scripts/Login.php") { Content = content, };

var response = await client.SendAsync(message);
response.EnsureSuccessStatusCode();

if (response.Content.Headers.ContentLength == 0) throw new Exception("Login failed");

var loginInfoResponseContent = await response.Content.ReadAsStringAsync();
if(!loginInfoResponseContent.Equals("[[2,\"\",false]]")) throw new Exception("Login failed");

response = await client.GetAsync("json.php");

var json = await response.Content.ReadAsStringAsync();

Console.WriteLine($"Json response: {Environment.NewLine}{json}");
