import React, { useState } from "react";
import { Form, Button, Modal } from "react-bootstrap";

const PageModal = (props) => {
  return (
    <div>
      <Modal.Dialog className="pg-modal">
        <Modal.Header closeButton>
          <Modal.Title>Modal title</Modal.Title>
        </Modal.Header>

        <Modal.Body>
          <p>Modal body text goes here.</p>
        </Modal.Body>

        <Modal.Footer>
          <Button variant="secondary">Close</Button>
          <Button variant="primary">Save changes</Button>
        </Modal.Footer>
      </Modal.Dialog>
    </div>
  );
};

export default PageModal;
