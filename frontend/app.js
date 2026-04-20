let isPaid = false;
let lastSuggestions = [];
let lastScore = 0;

function startQuiz() {
  document.getElementById("quiz").classList.remove("hidden");
}



async function getResult() {
  let interest = document.getElementById("interest").value;
  let skill = document.getElementById("skill").value;

  let response = await fetch("https://gethired-r3ho.onrender.com/get-career", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ interest, skill }),
  });

  let data = await response.json();

  document.getElementById("career").innerText = data.career;
  document.getElementById("desc").innerText = data.desc;

  document.getElementById("result").classList.remove("hidden");
}

function goToResume() {
  window.location.href = "resume.html";
}

// 🔥 Resume Analyzer (FINAL CLEAN VERSION)
async function uploadResume() {
  let fileInput = document.getElementById("resumeFile");
  let file = fileInput.files[0];

  if (!file) {
    alert("Please upload a resume first");
    return;
  }

  let formData = new FormData();
  formData.append("file", file);

  let response = await fetch("https://gethired-r3ho.onrender.com/analyze-resume", {
    method: "POST",
    body: formData,
  });

  let data = await response.json();

  // ✅ Store data globally
  lastSuggestions = data.suggestions;
  lastScore = data.score;

  // ✅ Render UI using function
  renderUI();
}

// 🔒 Unlock function
async function unlock() {
  try {
    // 1. Create order from backend
    let res = await fetch("https://gethired-r3ho.onrender.com/create-order", {
      method: "POST"
    });

    let order = await res.json();

    // 2. Razorpay options
    var options = {
      key: "rzp_test_SeXNvfHZuri6zn",
      amount: order.amount,
      currency: "INR",
      name: "AI Job Accelerator",
      description: "Unlock Full Resume Report",
      order_id: order.id,

      handler: function (response) {
        console.log("Payment Response:", response);

        alert("Payment Successful 🎉");

        // ✅ VERY IMPORTANT
        unlockContent();
      },

      modal: {
        ondismiss: function () {
          console.log("Payment popup closed");
        }
      }
    };

    var rzp = new Razorpay(options);
    rzp.open();

  } catch (err) {
    console.error("Payment Error:", err);
    alert("Something went wrong with payment");
  }
}



function unlockContent() {
  isPaid = true;

  renderUI(); // 🔥 THIS updates UI

  alert("Full report unlocked 🚀");
}


function renderUI() {
  document.getElementById("scoreBox").innerText = "Score: " + lastScore;

  let list = document.getElementById("suggestions");
  list.innerHTML = "";

  lastSuggestions.forEach((s, index) => {
    let li = document.createElement("li");

    if (!isPaid && index > 1) {
      li.innerText = "🔒 Unlock to see more";
    } else {
      li.innerText = s;
    }

    list.appendChild(li);
  });
}

async function rewriteResume() {
    const fileInput = document.getElementById("resumeFile");
    const file = fileInput.files[0];

    if (!file) {
        alert("Please upload a resume first");
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
        const response = await fetch("https://gethired-r3ho.onrender.com/rewrite", {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (data.error) {
            alert(data.error);
            return;
        }

        document.getElementById("result").innerHTML = data.rewritten_resume;

    } catch (error) {
        console.error(error);
        alert("Something went wrong");
    }
}