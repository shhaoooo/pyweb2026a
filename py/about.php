<!DOCTYPE html>
<html lang="zh-TW">
<head>
     <meta charset="UTF-8">
     <meta name="viewport" content="width=device-width, initial-scale=1.0">
     <title>洪唯皓簡介</title>
     <style type="text/css">
          * { font-family:"標楷體"; margin-left:auto; margin-right:auto;}
          h1 {color:blue; font-size:60px;}
          h2 {color:#33ff33; font-size:40px;}
     </style>

     <script>
          function change1() {
               document.getElementById("pic").src = "mountain.jpg";
               document.getElementById("h2text").innerText = "靜宜資管";
          }

          function change2() {
               document.getElementById("pic").src = "cliff.jpg";
               document.getElementById("h2text").innerText = "Wei-Hao Hong";
          }
     </script>
</head>
<body>
     <?php echo date("Y-m-d") ?>
     <table width="70%">
         <tr>
             <td>
                 <img src="cliff.jpg" width="110%" id="pic" onmouseover="change1()" onmouseout="change2()">
             </td>

             <td>
                 <h1>洪唯皓</h1>
                 <h2 id="h2text">>Wei-Hao Hong</h2>
             </td>
         </tr>
     </table>

     <br>

     <table width="70%" border="1">
          <tr>
               <td>
                    IG：<a href="https://www.instagram.com/_xuzbekistanx?igsh=aXU5aXB4eGw2Z3Nq&utm_source=qr" target="_blank">
                    https://www.instagram.com/_xuzbekistanx?igsh=aXU5aXB4eGw2Z3Nq&utm_source=qr</a><br>

                    E-Mail: <a href="mailto:asd0965104898@gmail.com">
                    asd0965104898@gmail.com</a><br>
               </td>

               <td>
                    大象席地而坐電影配樂<br>
                    <audio controls>
                         <source src="elephant.mp3" type="audio/mp3">
                    </audio><br>
               </td>

               <td>
                    不要去臺灣<br>
                    <iframe src="https://www.youtube.com/embed/pW88QFpHXa8"
                            width="300" height="200"
                            allowfullscreen>
                    </iframe>
               </td>
          </tr>
     </table>

</body>
</html>