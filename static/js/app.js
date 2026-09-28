// ===============================
// API HELPER
// ===============================

async function api(url, options = {}) {

    const isFormData =
        options.body instanceof FormData;

    const response = await fetch(url, {
        credentials: "include",
        ...options,

        headers: {
            ...(isFormData
                ? {}
                : {
                    "Content-Type": "application/json"
                }),

            ...(options.headers || {})
        }
    });

    const data =
        await response.json().catch(() => ({}));

    if (!response.ok) {
        throw new Error(
            data.detail || "Request failed"
        );
    }

    return data;
}


// ===============================
// MESSAGE
// ===============================

function showMessage(
    id,
    message,
    type = "error"
) {

    const element =
        document.getElementById(id);

    if (!element) return;

    element.className = type;

    element.textContent = message;

    element.classList.remove("hidden");
}


// ===============================
// SECURITY / HTML ESCAPING
// ===============================

function escapeHtml(value) {

    return String(value ?? "")
        .replace(/[&<>"']/g, character => ({
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#039;"
        }[character]));
}


function escapeAttr(value) {
    return escapeHtml(value);
}


// ===============================
// RENDER RECOMMENDATIONS
// ===============================

function renderRecommendations(
    result,
    targetId = "results"
) {

    const target =
        document.getElementById(targetId);

    if (!target) return;


    const cards =
        (result.recommendations || [])
        .map(item => `

            <div class="rec">

                <span class="badge">
                    ${escapeHtml(item.platform)}
                </span>

                <h3>
                    ${escapeHtml(item.name)}
                </h3>

                <p class="muted">
                    ${escapeHtml(item.category)}
                </p>

                <div class="price">
                    ₹${Number(
                        item.estimated_price || 0
                    ).toLocaleString("en-IN")}
                </div>

                <p>
                    ${escapeHtml(item.reason)}
                </p>

                ${
                    item.link
                        ? `
                        <a
                            class="btn secondary"
                            target="_blank"
                            rel="noopener"
                            href="${escapeAttr(item.link)}"
                        >
                            View / Search
                        </a>
                        `
                        : ""
                }

            </div>

        `)
        .join("");


    target.innerHTML = `

        <div class="panel">

            <span class="badge">
                ${
                    result.ai_powered
                        ? "Gemini AI"
                        : "Fallback Catalog"
                }
            </span>

            <h2>
                ${escapeHtml(result.title)}
            </h2>

            <p>
                ${escapeHtml(result.summary)}
            </p>


            <div class="two">

                <div>
                    <b>Budget:</b>

                    ₹${Number(
                        result.budget || 0
                    ).toLocaleString("en-IN")}
                </div>


                <div>
                    <b>Estimated total:</b>

                    ₹${Number(
                        result.estimated_total || 0
                    ).toLocaleString("en-IN")}
                </div>

            </div>


            <p>
                <b>Remaining:</b>

                ₹${Number(
                    result.budget_remaining || 0
                ).toLocaleString("en-IN")}
            </p>


            <div class="rec-grid">

                ${
                    cards ||
                    "<p>No recommendations found.</p>"
                }

            </div>


            <small class="muted">
                ${escapeHtml(
                    result.disclaimer || ""
                )}
            </small>


            <br>
            <br>


            <!-- SAVE PLAN BUTTON -->

            <button
                id="save-plan-button"
                class="btn"
                type="button"
                onclick="saveCurrentPlan()"
            >
                💾 Save Plan
            </button>


            <div
                id="save-message"
                class="hidden"
                style="margin-top:15px"
            ></div>

        </div>
    `;


    // Store current recommendation
    window.currentRecommendation = result;
}


// ===============================
// SAVE CURRENT PLAN
// ===============================

async function saveCurrentPlan() {

    const result =
        window.currentRecommendation;


    if (
        !result ||
        !result.recommendation_id
    ) {

        alert(
            "Please generate a recommendation first."
        );

        return;
    }


    const button =
        document.getElementById(
            "save-plan-button"
        );


    const message =
        document.getElementById(
            "save-message"
        );


    try {

        if (button) {

            button.disabled = true;

            button.textContent =
                "Saving...";
        }


        await api(
            "/api/save-plan",
            {
                method: "POST",

                body: JSON.stringify({
                    recommendation_id:
                        result.recommendation_id
                })
            }
        );


        if (message) {

            message.className =
                "success";

            message.textContent =
                "✅ Plan saved successfully!";

            message.classList.remove(
                "hidden"
            );
        }


        if (button) {

            button.textContent =
                "✅ Plan Saved";
        }


    } catch (error) {

        if (message) {

            message.className =
                "error";

            message.textContent =
                error.message;

            message.classList.remove(
                "hidden"
            );
        }


        if (button) {

            button.disabled = false;

            button.textContent =
                "💾 Save Plan";
        }
    }
}


// ===============================
// HOME ITEM
// ===============================

function addHomeItem() {

    const container =
        document.getElementById(
            "home-items"
        );

    if (!container) return;


    const row =
        document.createElement("div");

    row.className =
        "item-row";


    row.innerHTML = `

        <input
            class="input item-category"
            placeholder="Example: Table"
        >


        <input
            class="input item-qty"
            type="number"
            min="1"
            value="1"
        >


        <button
            class="btn secondary"
            type="button"
            onclick="this.parentElement.remove()"
        >
            ×
        </button>

    `;


    container.appendChild(row);
}


// ===============================
// HOME PLANNER
// ===============================

async function submitHome(event) {

    event.preventDefault();


    try {

        const budget =
            Number(
                document.getElementById(
                    "budget"
                ).value
            );


        const rooms =
            document
                .getElementById("rooms")
                .value
                .split(",")
                .map(item =>
                    item.trim()
                )
                .filter(Boolean);


        const style =
            document.getElementById(
                "style"
            ).value;


        const notes =
            document.getElementById(
                "notes"
            ).value;


        const rows =
            document.querySelectorAll(
                "#home-items .item-row"
            );


        const items = [];


        rows.forEach(row => {

            const categoryInput =
                row.querySelector(
                    ".item-category"
                );


            const quantityInput =
                row.querySelector(
                    ".item-qty"
                );


            const category =
                categoryInput
                    ? categoryInput.value.trim()
                    : "";


            const quantity =
                quantityInput
                    ? Number(
                        quantityInput.value
                    )
                    : 1;


            if (category) {

                items.push({
                    category: category,
                    quantity: quantity
                });
            }
        });


        const payload = {

            budget: budget,

            rooms: rooms,

            style: style,

            notes: notes,

            items: items
        };


        showMessage(
            "message",
            "Generating your Home recommendations...",
            "success"
        );


        const result =
            await api(
                "/api/generate-home",
                {
                    method: "POST",

                    body:
                        JSON.stringify(
                            payload
                        )
                }
            );


        renderRecommendations(
            result
        );


        showMessage(
            "message",
            "Recommendation generated successfully!",
            "success"
        );


    } catch (error) {

        showMessage(
            "message",
            error.message,
            "error"
        );
    }
}


// ===============================
// PARTY PLANNER
// ===============================

async function submitParty(event) {

    event.preventDefault();


    try {

        const budget =
            Number(
                document.getElementById(
                    "budget"
                ).value
            );


        const guests =
            Number(
                document.getElementById(
                    "guests"
                ).value
            );


        const eventType =
            document.getElementById(
                "event_type"
            ).value;


        const venue =
            document.getElementById(
                "venue"
            ).value;


        const notes =
            document.getElementById(
                "notes"
            ).value;


        const payload = {

            budget: budget,

            guests: guests,

            event_type: eventType,

            venue: venue,

            notes: notes
        };


        showMessage(
            "message",
            "Generating your Party recommendations...",
            "success"
        );


        const result =
            await api(
                "/api/generate-party",
                {
                    method: "POST",

                    body:
                        JSON.stringify(
                            payload
                        )
                }
            );


        renderRecommendations(
            result
        );


        showMessage(
            "message",
            "Party recommendation generated successfully!",
            "success"
        );


    } catch (error) {

        showMessage(
            "message",
            error.message,
            "error"
        );
    }
}


// ===============================
// JEWELRY PLANNER
// ===============================

async function submitJewelry(event) {

    event.preventDefault();


    try {

        const form =
            document.getElementById(
                "jewelry-form"
            );


        const formData =
            new FormData(form);


        showMessage(
            "message",
            "Generating your Jewelry recommendations...",
            "success"
        );


        const result =
            await api(
                "/api/generate-jewelry",
                {
                    method: "POST",

                    body: formData
                }
            );


        renderRecommendations(
            result
        );


        showMessage(
            "message",
            "Jewelry recommendation generated successfully!",
            "success"
        );


    } catch (error) {

        showMessage(
            "message",
            error.message,
            "error"
        );
    }
}


// ===============================
// LOGIN
// ===============================

async function login(event) {

    event.preventDefault();


    try {

        const email =
            document.getElementById(
                "email"
            ).value;


        const password =
            document.getElementById(
                "password"
            ).value;


        const result =
            await api(
                "/api/auth/login",
                {
                    method: "POST",

                    body:
                        JSON.stringify({
                            email: email,
                            password: password
                        })
                }
            );


        showMessage(
            "message",
            result.message ||
            "Login successful!",
            "success"
        );


        setTimeout(() => {

            window.location.href =
                "/dashboard";

        }, 700);


    } catch (error) {

        showMessage(
            "message",
            error.message,
            "error"
        );
    }
}


// ===============================
// REGISTER
// ===============================

async function register(event) {

    event.preventDefault();


    try {

        const name =
            document.getElementById(
                "name"
            ).value;


        const email =
            document.getElementById(
                "email"
            ).value;


        const password =
            document.getElementById(
                "password"
            ).value;


        const result =
            await api(
                "/api/auth/register",
                {
                    method: "POST",

                    body:
                        JSON.stringify({
                            name: name,
                            email: email,
                            password: password
                        })
                }
            );


        showMessage(
            "message",
            result.message ||
            "Registration successful!",
            "success"
        );


        setTimeout(() => {

            window.location.href =
                "/login";

        }, 700);


    } catch (error) {

        showMessage(
            "message",
            error.message,
            "error"
        );
    }
}


// ===============================
// DASHBOARD
// ===============================

async function loadDashboard() {

    try {

        const result =
            await api(
                "/api/session-info"
            );


        const userName =
            document.getElementById(
                "user-name"
            );


        if (
            userName &&
            result.user
        ) {

            userName.textContent =
                result.user.name ||
                result.user.email ||
                "User";
        }


    } catch (error) {

        console.error(
            "Dashboard error:",
            error
        );
    }
}


// ===============================
// HISTORY
// ===============================

async function loadHistory() {

    const container =
        document.getElementById(
            "history-list"
        );


    if (!container) return;


    try {

        const history =
            await api(
                "/api/history"
            );


        if (
            !history ||
            history.length === 0
        ) {

            container.innerHTML = `

                <div class="panel">

                    <h3>
                        No recommendations yet.
                    </h3>

                    <p class="muted">
                        Generate a Home, Party or
                        Jewelry recommendation
                        to see it here.
                    </p>

                </div>

            `;

            return;
        }


        container.innerHTML =
            history
                .map(item => {

                    const response =
                        item.response || {};


                    const request =
                        item.request || {};


                    let extraDetails = "";


                    if (
                        item.planner_type ===
                        "home"
                    ) {

                        extraDetails = `

                            <p>
                                <b>Rooms:</b>

                                ${escapeHtml(
                                    Array.isArray(
                                        request.rooms
                                    )
                                        ? request.rooms.join(
                                            ", "
                                        )
                                        : request.rooms ||
                                          "-"
                                )}

                            </p>


                            <p>
                                <b>Style:</b>

                                ${escapeHtml(
                                    request.style ||
                                    "-"
                                )}

                            </p>

                        `;
                    }


                    if (
                        item.planner_type ===
                        "party"
                    ) {

                        extraDetails = `

                            <p>
                                <b>Event:</b>

                                ${escapeHtml(
                                    request.event_type ||
                                    "-"
                                )}

                            </p>


                            <p>
                                <b>Guests:</b>

                                ${escapeHtml(
                                    request.guests ||
                                    "-"
                                )}

                            </p>

                        `;
                    }


                    if (
                        item.planner_type ===
                        "jewelry"
                    ) {

                        extraDetails = `

                            <p>
                                <b>Occasion:</b>

                                ${escapeHtml(
                                    request.occasion ||
                                    "-"
                                )}

                            </p>


                            <p>
                                <b>Style:</b>

                                ${escapeHtml(
                                    request.style ||
                                    "-"
                                )}

                            </p>

                        `;
                    }


                    return `

                        <div class="panel">

                            <span class="badge">

                                ${escapeHtml(
                                    item.planner_type
                                ).toUpperCase()}

                            </span>


                            <h2>

                                ${escapeHtml(
                                    response.title ||
                                    "Recommendation"
                                )}

                            </h2>


                            <p>

                                ${escapeHtml(
                                    response.summary ||
                                    ""
                                )}

                            </p>


                            <p>

                                <b>Budget:</b>

                                ₹${Number(
                                    response.budget ||
                                    0
                                ).toLocaleString(
                                    "en-IN"
                                )}

                            </p>


                            <p>

                                <b>Estimated total:</b>

                                ₹${Number(
                                    response.estimated_total ||
                                    0
                                ).toLocaleString(
                                    "en-IN"
                                )}

                            </p>


                            ${extraDetails}


                            <p class="muted">

                                Generated on:

                                ${escapeHtml(
                                    item.created_at ||
                                    "-"
                                )}

                            </p>


                            <button
                                class="btn secondary"
                                type="button"
                                onclick="viewRecommendation(${item.id})"
                            >
                                View Details
                            </button>


                            <button
                                class="btn secondary"
                                type="button"
                                onclick="deleteHistory(${item.id})"
                            >
                                Delete
                            </button>

                        </div>

                    `;

                })
                .join("");


    } catch (error) {

        container.innerHTML = `

            <div class="panel">

                <p>
                    ${escapeHtml(
                        error.message
                    )}
                </p>

            </div>

        `;
    }
}


// ===============================
// VIEW HISTORY DETAILS
// ===============================

async function viewRecommendation(id) {

    try {

        const result =
            await api(
                `/api/history/${id}`
            );


        const response =
            result.response || {};


        let message = "";


        message +=
            `Title: ${
                response.title || "-"
            }\n\n`;


        message +=
            `Summary: ${
                response.summary || "-"
            }\n\n`;


        message +=
            `Budget: ₹${
                Number(
                    response.budget || 0
                ).toLocaleString("en-IN")
            }\n`;


        message +=
            `Estimated Total: ₹${
                Number(
                    response.estimated_total ||
                    0
                ).toLocaleString("en-IN")
            }\n`;


        message +=
            `Remaining: ₹${
                Number(
                    response.budget_remaining ||
                    0
                ).toLocaleString("en-IN")
            }\n\n`;


        if (
            response.recommendations
        ) {

            message +=
                "Recommendations:\n\n";


            response.recommendations
                .forEach(
                    (item, index) => {

                        message +=
                            `${index + 1}. ${
                                item.name
                            }\n`;

                        message +=
                            `Platform: ${
                                item.platform
                            }\n`;

                        message +=
                            `Price: ₹${
                                Number(
                                    item.estimated_price ||
                                    0
                                ).toLocaleString(
                                    "en-IN"
                                )
                            }\n\n`;
                    }
                );
        }


        alert(message);


    } catch (error) {

        alert(error.message);
    }
}


// ===============================
// DELETE HISTORY
// ===============================

async function deleteHistory(id) {

    const confirmDelete =
        confirm(
            "Are you sure you want to delete this recommendation?"
        );


    if (!confirmDelete) return;


    try {

        await api(
            `/api/history/${id}`,
            {
                method: "DELETE"
            }
        );


        await loadHistory();


    } catch (error) {

        alert(error.message);
    }
}